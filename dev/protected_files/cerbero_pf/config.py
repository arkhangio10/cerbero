"""Configuración: archivo TOML sin secretos; la clave maestra vive en un archivo aparte."""
from __future__ import annotations

import ipaddress
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
HARD_MAX_PLAINTEXT = 8 * 1024 * 1024
GEO_PROVIDERS = ("none", "csv", "simulated")


class ConfigError(ValueError):
    pass


def is_loopback_host(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host.strip("[]")).is_loopback
    except ValueError:
        return False


@dataclass(frozen=True)
class SmtpConfig:
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8025
    sender: str = "cerbero-pf@localhost"
    starttls: bool = False
    username: str = ""
    password_env: str = "CERBERO_PF_SMTP_PASSWORD"
    allow_external: bool = False
    timeout_seconds: float = 10.0
    max_attempts: int = 5
    retry_base_seconds: float = 30.0
    poll_seconds: float = 2.0
    hourly_cap_per_owner: int = 10


@dataclass(frozen=True)
class Config:
    data_dir: Path
    master_key_file: Path
    host: str = "127.0.0.1"
    port: int = 8765
    public_base_url: str = ""
    allow_non_loopback: bool = False
    cookie_secure: bool = False
    allowed_hosts: tuple[str, ...] = ("127.0.0.1", "localhost")
    trusted_proxies: tuple[str, ...] = ()
    export_roots: tuple[Path, ...] = ()
    export_output_dir: Path | None = None
    max_plaintext_bytes: int = 1024 * 1024
    session_hours: float = 8.0
    login_max_failures: int = 5
    login_window_minutes: float = 15.0
    open_attempts_per_minute: int = 30
    dedup_window_minutes: float = 15.0
    geo_provider: str = "none"
    geo_csv_path: Path | None = None
    smtp: SmtpConfig = field(default_factory=SmtpConfig)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "cerbero_pf.sqlite3"

    @property
    def containers_dir(self) -> Path:
        return self.data_dir / "containers"

    @property
    def base_url(self) -> str:
        return self.public_base_url or f"http://{self.host}:{self.port}"

    def validate(self) -> "Config":
        if not is_loopback_host(self.host) and not self.allow_non_loopback:
            raise ConfigError(f"host {self.host!r} no es loopback; fuera del equipo hace falta HTTPS y "
                              "una revisión de seguridad (allow_non_loopback = true sólo tras hacerla)")
        if not 0 < self.max_plaintext_bytes <= HARD_MAX_PLAINTEXT:
            raise ConfigError(f"max_plaintext_bytes debe estar entre 1 y {HARD_MAX_PLAINTEXT}")
        key = self.master_key_file.resolve()
        for forbidden, label in ((self.data_dir.resolve(), "el directorio de datos"), (STATIC_DIR, "el directorio público")):
            if key.is_relative_to(forbidden):
                raise ConfigError(f"la clave maestra no puede estar dentro de {label} ({forbidden})")
        if self.geo_provider not in GEO_PROVIDERS:
            raise ConfigError(f"geo.provider debe ser uno de {GEO_PROVIDERS}")
        if self.geo_provider == "csv" and not (self.geo_csv_path and self.geo_csv_path.is_file()):
            raise ConfigError("geo.provider = 'csv' requiere geo.csv_path con un archivo existente")
        for proxy in self.trusted_proxies:
            try:
                ipaddress.ip_network(proxy, strict=False)
            except ValueError:
                raise ConfigError(f"proxy de confianza inválido: {proxy!r}") from None
        if self.smtp.enabled and not is_loopback_host(self.smtp.host) and not self.smtp.allow_external:
            raise ConfigError("el envío SMTP a un servidor externo está desactivado; configura destinatarios y "
                              "servicio y pon smtp.allow_external = true conscientemente")
        if self.smtp.max_attempts < 1:
            raise ConfigError("smtp.max_attempts debe ser al menos 1")
        return self


def load_config(path: Path) -> Config:
    path = Path(path).resolve()
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    base = path.parent

    def rel(value: str | None) -> Path | None:
        return (base / value).resolve() if value else None

    server, storage = raw.get("server", {}), raw.get("storage", {})
    limits, geo, notes = raw.get("limits", {}), raw.get("geo", {}), raw.get("notifications", {})
    if "data_dir" not in storage or "master_key_file" not in storage:
        raise ConfigError("storage.data_dir y storage.master_key_file son obligatorios")
    smtp = SmtpConfig(**raw.get("smtp", {}))
    return Config(
        data_dir=rel(storage["data_dir"]),
        master_key_file=rel(storage["master_key_file"]),
        host=server.get("host", "127.0.0.1"),
        port=int(server.get("port", 8765)),
        public_base_url=server.get("public_base_url", ""),
        allow_non_loopback=bool(server.get("allow_non_loopback", False)),
        cookie_secure=bool(server.get("cookie_secure", False)),
        allowed_hosts=tuple(server.get("allowed_hosts", ("127.0.0.1", "localhost"))),
        trusted_proxies=tuple(server.get("trusted_proxies", ())),
        export_roots=tuple(rel(p) for p in storage.get("export_roots", ())),
        export_output_dir=rel(storage.get("export_output_dir")),
        max_plaintext_bytes=int(limits.get("max_plaintext_bytes", 1024 * 1024)),
        session_hours=float(limits.get("session_hours", 8)),
        login_max_failures=int(limits.get("login_max_failures", 5)),
        login_window_minutes=float(limits.get("login_window_minutes", 15)),
        open_attempts_per_minute=int(limits.get("open_attempts_per_minute", 30)),
        dedup_window_minutes=float(notes.get("dedup_window_minutes", 15)),
        geo_provider=geo.get("provider", "none"),
        geo_csv_path=rel(geo.get("csv_path")),
        smtp=smtp,
    ).validate()
