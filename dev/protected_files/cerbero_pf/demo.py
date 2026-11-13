"""Demo reproducible con datos sintéticos: servidor real en otro proceso, SQLite real, buzón SMTP local y reinicio.

Pasos:
 1. Exportar un documento a .cerbero y comprobar que el original no cambia.
 2. Abrirlo como lector autorizado y ver el evento real.
 3. Marcarlo como extraviado desde la cuenta propietaria.
 4. Intentar abrir una copia desde otra sesión: denegación, evento y aviso.
 5. Ver el mensaje en el buzón SMTP local y su estado de entrega real.
 6. Reiniciar el servicio y comprobar que la revocación y los eventos permanecen.
"""
from __future__ import annotations

import base64
import hashlib
import json
import secrets
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx

from .config import load_config
from .crypto import generate_master_key_file
from .geo import describe_location
from .mail import read_mailbox, start_mailbox
from .service import RequestContext, Service, ServiceError

MARKER = ".cerbero-pf-demo"
PROJECT_DIR = Path(__file__).resolve().parents[1]
SYNTHETIC_TEXT = (
    "CONTRATO DE SERVICIOS DE DISEÑO (documento sintético de demostración)\n\n"
    "Partes: Estudio Ficticio Aurora y Cliente de Ejemplo. Ningún dato corresponde a personas reales.\n"
    "Objeto: entrega 2 del proyecto Aurora. Importe: 0,00 (ejemplo).\n"
)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_config(path: Path, port: int, mail_port: int | None, geo: str = "none") -> None:
    smtp = (f"[smtp]\nenabled = true\nhost = \"127.0.0.1\"\nport = {mail_port}\nsender = \"cerbero-pf@demo.invalid\"\n"
            "retry_base_seconds = 1\npoll_seconds = 0.5\nmax_attempts = 5\n") if mail_port else "[smtp]\nenabled = false\n"
    path.write_text(
        "# Configuración generada por la demo. Sin secretos: la clave maestra está en secrets/master.key.\n"
        f"[server]\nhost = \"127.0.0.1\"\nport = {port}\n\n"
        "[storage]\ndata_dir = \"data\"\nmaster_key_file = \"secrets/master.key\"\n"
        "export_roots = [\"nas\"]\nexport_output_dir = \"exports\"\n\n"
        f"[geo]\nprovider = \"{geo}\"\n\n{smtp}", encoding="utf-8")


class _Server:
    def __init__(self, config: Path, log: Path, port: int):
        self.config, self.log, self.base = config, log, f"http://127.0.0.1:{port}"
        self.proc = None

    def start(self) -> None:
        handle = self.log.open("ab")
        self.proc = subprocess.Popen([sys.executable, "-m", "cerbero_pf", "serve", "--config", str(self.config)],
                                     cwd=PROJECT_DIR, stdout=handle, stderr=subprocess.STDOUT)
        handle.close()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError(f"el servicio terminó al arrancar; revisa {self.log}")
            try:
                if httpx.get(f"{self.base}/api/health", timeout=1).status_code == 200:
                    return
            except httpx.HTTPError:
                time.sleep(0.2)
        raise RuntimeError("el servicio no respondió a tiempo")

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()  # en Windows es una terminación abrupta: también prueba la durabilidad
            self.proc.wait(timeout=15)


class _Report:
    def __init__(self):
        self.lines: list[str] = []
        self.checks: list[dict] = []

    def say(self, text: str = "") -> None:
        print(text, flush=True)
        self.lines.append(text)

    def check(self, step: str, label: str, ok: bool, evidence) -> None:
        self.checks.append({"step": step, "check": label, "ok": bool(ok), "evidence": evidence})
        self.say(f"   [{'OK' if ok else 'FALLO'}] {label}: {evidence}")


def _login(base: str, username: str, password: str) -> httpx.Client:
    client = httpx.Client(base_url=base, timeout=15)
    response = client.post("/api/login", json={"username": username, "password": password})
    response.raise_for_status()
    client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    return client


def _prepare(out: Path, fresh: bool) -> None:
    out = out.resolve()
    if out.exists() and any(out.iterdir()):
        if not fresh:
            raise ServiceError(409, "demo_exists", f"ya existe una demo en {out}; usa --fresh para reemplazarla")
        if not (out / MARKER).is_file():
            raise ServiceError(409, "not_demo", f"{out} no tiene la marca {MARKER}; no se borra")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / MARKER).write_text("Datos sintéticos de la demo de cerbero_pf. Se pueden borrar.\n", encoding="utf-8")


def run_demo(out: Path, fresh: bool = False, keep_running: bool = False, simulated_geo: bool = False) -> dict:
    out = Path(out).resolve()
    _prepare(out, fresh)
    report = _Report()
    for name in ("secrets", "data", "mailbox", "nas", "exports", "copia"):
        (out / name).mkdir(exist_ok=True)
    original = out / "nas" / "Contrato.txt"
    original.write_bytes(SYNTHETIC_TEXT.encode("utf-8"))
    port, mail_port = _free_port(), _free_port()
    config = out / "config.toml"
    _write_config(config, port, mail_port)
    cfg = load_config(config)
    key_id = generate_master_key_file(cfg.master_key_file)
    service = Service(cfg)
    passwords = {name: secrets.token_urlsafe(12) for name in ("propietario", "lector", "tercero")}
    service.create_user("propietario", passwords["propietario"], "Propietaria de ejemplo", "propietario@demo.invalid")
    service.create_user("lector", passwords["lector"], "Lector autorizado")
    service.create_user("tercero", passwords["tercero"], "Tercero sin permiso")
    (out / "credentials.txt").write_text(
        "Cuentas SINTÉTICAS de la demo (contraseñas aleatorias de esta ejecución):\n"
        + "".join(f"{u}: {p}\n" for u, p in passwords.items()), encoding="utf-8")

    report.say(f"Demo de Cerbero: archivos protegidos (datos sintéticos en {out})")
    report.say(f"Clave maestra nueva {key_id} en {cfg.master_key_file}, separada de {cfg.data_dir}.")
    mailbox = start_mailbox(out / "mailbox", "127.0.0.1", mail_port)
    server = _Server(config, out / "server.log", port)
    clients: list[httpx.Client] = []
    try:
        server.start()
        report.say(f"Servicio en {server.base} (proceso {server.proc.pid}); buzón SMTP local en 127.0.0.1:{mail_port}.")

        report.say("\n1. Exportar Contrato.txt a .cerbero")
        before = (_sha(original), original.stat().st_mtime_ns)
        owner = _login(server.base, "propietario", passwords["propietario"])
        clients.append(owner)
        created = owner.post("/api/documents", content=original.read_bytes(), headers={"X-Filename": "Contrato.txt"})
        created.raise_for_status()
        doc = created.json()["document"]
        container = owner.get(created.json()["container_url"]).content
        exported = out / "exports" / doc["container_name"]
        exported.write_bytes(container)
        after = (_sha(original), original.stat().st_mtime_ns)
        report.check("1", "el original no cambia (SHA-256 y fecha de modificación)", before == after, before[0][:16])
        report.check("1", "el contenedor no contiene el texto legible", SYNTHETIC_TEXT.encode()[:40] not in container,
                     f"{exported.name}, {len(container)} bytes, SHA-256 {doc['container_sha256'][:16]}…")

        report.say("\n2. Abrir como lector autorizado")
        owner.post(f"/api/documents/{doc['id']}/grants", json={"username": "lector"}).raise_for_status()
        reader = _login(server.base, "lector", passwords["lector"])
        clients.append(reader)
        opened = reader.post("/api/open", content=exported.read_bytes())
        body = opened.json()
        report.check("2", "el lector obtiene exactamente los bytes originales",
                     opened.status_code == 200 and base64.b64decode(body.get("content_b64", "")) == original.read_bytes(),
                     f"HTTP {opened.status_code}, {body['message']}")
        served = [e for e in owner.get("/api/events").json()["events"] if e["kind"] == "content_served"]
        report.check("2", "el propietario ve el evento real", bool(served) and served[0]["actor_label"] == "lector",
                     f"evento {served[0]['id']} a las {served[0]['at_utc']}, IP {served[0]['ip']}, "
                     f"ubicación {served[0]['geo_text']}" if served else "sin evento")

        report.say("\n3. Marcar como extraviado")
        marked = owner.post(f"/api/documents/{doc['id']}/state", json={"state": "lost", "confirm_doc_id": doc["id"]})
        marked.raise_for_status()
        effective = marked.json()["document"]["effective_at"]
        report.check("3", "la operación quedó confirmada y persistida", marked.json()["document"]["state"] == "lost",
                     f"efectiva desde {effective}")

        report.say("\n4. Abrir una copia desde otra sesión")
        copy = out / "copia" / "Contrato (copia).cerbero"
        shutil.copyfile(exported, copy)
        third = _login(server.base, "tercero", passwords["tercero"])
        clients.append(third)
        denied = third.post("/api/open", content=copy.read_bytes())
        report.check("4", "la copia se deniega a la cuenta tercera",
                     denied.status_code == 403 and denied.json()["reason"] == "document_lost" and "content_b64" not in denied.json(),
                     f"HTTP {denied.status_code}, {denied.json()['message']}")
        again = reader.post("/api/open", content=exported.read_bytes())
        report.check("4", "la sesión del lector abierta antes también queda denegada",
                     again.status_code == 403 and "content_b64" not in again.json(), f"HTTP {again.status_code}")
        notes = owner.get("/api/notifications").json()["notifications"]
        mine = [n for n in notes if "tercero" in n["body"]]
        report.check("4", "evento y aviso para el propietario", bool(mine), mine[0]["body"] if mine else "sin aviso")

        report.say("\n5. Correo en el buzón SMTP local")
        deadline, status = time.monotonic() + 30, None
        while time.monotonic() < deadline:
            mine = [n for n in owner.get("/api/notifications").json()["notifications"] if "tercero" in n["body"]]
            status = mine[0]["email_status"] if mine else None
            if status in ("sent", "failed"):
                break
            time.sleep(0.5)
        report.check("5", "estado real en la cola: enviado (aceptado por el servidor SMTP)", status == "sent",
                     f"estado {status}, intentos {mine[0]['email_attempts'] if mine else '?'}")
        messages = [m for _, m in read_mailbox(out / "mailbox") if "Contrato.cerbero" in str(m["Subject"])]
        text = messages[0].get_content() if messages else ""
        report.check("5", "el mensaje llegó al buzón local", bool(messages),
                     f"{len(messages)} mensaje(s); asunto «{messages[0]['Subject']}»" if messages else "vacío")
        report.check("5", "el correo no incluye contenido ni claves", bool(text) and "Estudio Ficticio" not in text
                     and "master" not in text.lower(), text.strip().splitlines()[0] if text else "")

        report.say("\n6. Reiniciar el servicio")
        events_before = len(owner.get("/api/events").json()["events"])
        server.stop()
        down = None
        try:
            reader.post("/api/open", content=exported.read_bytes())
        except httpx.HTTPError as exc:
            down = type(exc).__name__
        report.check("6", "con el servicio detenido no hay apertura posible", down is not None, down)
        server.start()
        doc_after = owner.get(f"/api/documents/{doc['id']}").json()["document"]
        events_after = owner.get("/api/events").json()["events"]
        report.check("6", "el estado extraviado permanece", doc_after["state"] == "lost",
                     f"{doc_after['state']} desde {doc_after['state_changed_at']}")
        report.check("6", "los eventos permanecen", len(events_after) >= events_before,
                     f"{events_before} antes, {len(events_after)} después")
        late = reader.post("/api/open", content=copy.read_bytes())
        report.check("6", "la sesión anterior sigue sin poder leer tras reiniciar",
                     late.status_code == 403 and "content_b64" not in late.json(), f"HTTP {late.status_code}")

        if simulated_geo:
            _simulated_case(out / "geo-simulado", report)

        failed = [c for c in report.checks if not c["ok"]]
        report.say(f"\nResultado: {len(report.checks) - len(failed)}/{len(report.checks)} comprobaciones correctas.")
        report.say("Límites: el servidor registra solicitudes, no lecturas; la ubicación por IP es aproximada (en "
                   "localhost no hay ubicación); revocar no borra lo ya entregado; no se detecta descifrado fuera del "
                   "servicio porque la clave nunca sale de él.")
        summary = {"out": str(out), "base_url": server.base, "document": doc["id"], "checks": report.checks,
                   "passed": not failed}
        (out / "demo-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "demo-transcript.txt").write_text("\n".join(report.lines) + "\n", encoding="utf-8")
        if keep_running:
            report.say(f"\nPanel: {server.base}/panel   Visor: {server.base}/visor")
            report.say(f"Cuentas sintéticas en {out / 'credentials.txt'}. Ctrl+C para detener servicio y buzón.")
            try:
                while server.proc.poll() is None:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        return summary
    finally:
        for client in clients:
            client.close()
        server.stop()
        mailbox.stop()


def _simulated_case(out: Path, report: _Report) -> None:
    """Caso aparte: proveedor geográfico SIMULADO para enseñar el aspecto de la alerta. No es un resultado real."""
    report.say("\nCaso aparte: proveedor geográfico SIMULADO")
    for name in ("secrets", "data", "nas", "exports"):
        (out / name).mkdir(parents=True, exist_ok=True)
    config = out / "config.toml"
    _write_config(config, _free_port(), None, geo="simulated")
    cfg = load_config(config)
    generate_master_key_file(cfg.master_key_file)
    service = Service(cfg)
    owner_password, third_password = secrets.token_urlsafe(12), secrets.token_urlsafe(12)
    service.create_user("propietario", owner_password)
    service.create_user("tercero", third_password)
    _, owner = service.login("propietario", owner_password, "127.0.0.1")
    _, third = service.login("tercero", third_password, "127.0.0.1")
    doc, container = service.export_document(owner, "Contrato.txt", SYNTHETIC_TEXT.encode(), RequestContext(ip="127.0.0.1"))
    service.set_state(owner, doc["id"], "lost", doc["id"], RequestContext(ip="127.0.0.1"))
    result = service.open_container(container, third, RequestContext(ip="127.0.0.1"))
    note = service.notifications(owner)[0]
    event = service.events(owner)[0]
    report.check("SIMULADO", "la alerta marca la ubicación como SIMULADO",
                 result.result == "denied" and "SIMULADO" in note["body"], note["body"])
    report.say(f"   Ubicación registrada en el evento: {describe_location(event['geo'])}")
