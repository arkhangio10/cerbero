"""IP de la conexión, ubicación aproximada opcional y ubicación declarada por el navegador.

La ubicación por IP es aproximada, puede reflejar una VPN o un proxy y no identifica a una persona.
Por defecto no hay proveedor: nunca se consulta un servicio externo.
"""
from __future__ import annotations

import csv
import ipaddress
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .security import clean_text

UNAVAILABLE = "no disponible"


@dataclass(frozen=True)
class ClientAddress:
    ip: str
    source: str
    forwarded_raw: str


def _in_networks(ip: str, networks) -> bool:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(address in net for net in networks)


def client_address(peer: str | None, forwarded: str | None, trusted_proxies: tuple[str, ...]) -> ClientAddress:
    """`X-Forwarded-For` sólo cuenta si la conexión viene de un proxy configurado como confiable."""
    peer = peer or "desconocida"
    raw = clean_text(forwarded, 200)
    networks = [ipaddress.ip_network(p, strict=False) for p in trusted_proxies]
    if forwarded and _in_networks(peer, networks):
        for part in reversed([p.strip() for p in forwarded.split(",")][-20:]):
            try:
                hop = str(ipaddress.ip_address(part))
            except ValueError:
                break
            if not _in_networks(hop, networks):
                return ClientAddress(hop, "x-forwarded-for de proxy confiable", raw)
    return ClientAddress(peer, "conexión", raw)


def ip_class(ip: str) -> str:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return "inválida"
    if address.is_loopback:
        return "loopback"
    if address.is_link_local:
        return "enlace local"
    if address.is_private:
        return "privada"
    if address.is_global:
        return "pública"
    return "reservada"


class NoGeo:
    name = "none"

    def lookup(self, ip: str) -> dict | None:
        return None


class CsvGeo:
    """Base local opcional: CSV con `network,country,region,city,accuracy_radius_km` (p. ej. derivada de GeoLite2)."""

    name = "csv"

    def __init__(self, path: Path):
        self.rows = []
        with Path(path).open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                self.rows.append((ipaddress.ip_network(row["network"].strip(), strict=False), {
                    "country": clean_text(row.get("country"), 60),
                    "region": clean_text(row.get("region"), 80),
                    "city": clean_text(row.get("city"), 80),
                    "accuracy_radius_km": int(row["accuracy_radius_km"]) if row.get("accuracy_radius_km") else None,
                }))
        self.rows.sort(key=lambda item: item[0].prefixlen, reverse=True)

    def lookup(self, ip: str) -> dict | None:
        address = ipaddress.ip_address(ip)
        for network, record in self.rows:
            if address.version == network.version and address in network:
                return dict(record)
        return None


class SimulatedGeo:
    """Sólo para enseñar el aspecto de la alerta. Todo resultado lleva la marca SIMULADO."""

    name = "simulated"

    def lookup(self, ip: str) -> dict | None:
        return {"country": "País simulado", "region": "", "city": "Ciudad simulada", "accuracy_radius_km": 100}


def build_provider(name: str, csv_path: Path | None):
    if name == "csv":
        return CsvGeo(csv_path)
    if name == "simulated":
        return SimulatedGeo()
    return NoGeo()


def locate(ip: str, provider) -> dict:
    kind = ip_class(ip)
    if provider.name == "simulated":
        return {"status": "simulated", "label": "SIMULADO", "ip_class": kind, "source": "simulated",
                **provider.lookup(ip)}
    if kind != "pública":
        return {"status": "unavailable", "reason": f"IP {kind}", "ip_class": kind, "source": provider.name}
    if provider.name == "none":
        return {"status": "unavailable", "reason": "sin proveedor geográfico", "ip_class": kind, "source": "none"}
    found = provider.lookup(ip)
    if not found:
        return {"status": "unavailable", "reason": "sin resultado en la base local", "ip_class": kind,
                "source": provider.name}
    return {"status": "approximate", "ip_class": kind, "source": provider.name, **found}


def describe_location(geo: dict | None) -> str:
    if not geo or geo.get("status") not in ("approximate", "simulated"):
        return UNAVAILABLE
    place = ", ".join(p for p in (geo.get("city"), geo.get("region"), geo.get("country")) if p) or "sin nombre"
    radius = f", radio aprox. {geo['accuracy_radius_km']} km" if geo.get("accuracy_radius_km") else ""
    text = f"{place}{radius}; aproximada por IP, puede reflejar una VPN o un proxy"
    return f"SIMULADO — {text}" if geo["status"] == "simulated" else text


def _number(value, low: float, high: float) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        value = float(value)
    except OverflowError:
        return None
    return value if math.isfinite(value) and low <= value <= high else None


def client_location(raw: str | None, received_at: str) -> dict:
    """Ubicación declarada por el navegador. Es información del cliente y puede manipularse."""
    if not raw:
        return {"status": "not_requested"}
    base = {"provenance": "declarada por el cliente (navegador)", "received_at": received_at}
    try:
        data = json.loads(raw) if len(raw) <= 512 else None
    except json.JSONDecodeError:
        data = None
    if not isinstance(data, dict):
        return {"status": "invalid", **base}
    status = data.get("status")
    if status in ("denied", "unavailable"):
        return {"status": status, **base}
    if status != "granted":
        return {"status": "invalid", **base}
    lat, lon = _number(data.get("lat"), -90, 90), _number(data.get("lon"), -180, 180)
    accuracy = _number(data.get("accuracy_m"), 0.000001, 1_000_000)
    if lat is None or lon is None or accuracy is None:
        return {"status": "invalid", **base}
    result = {"status": "declared", **base, "lat": lat, "lon": lon, "accuracy_m": accuracy}
    stamp = _number(data.get("timestamp_ms"), 0, 32503680000000)
    if stamp is not None:
        result["reported_at"] = datetime.fromtimestamp(stamp / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    return result
