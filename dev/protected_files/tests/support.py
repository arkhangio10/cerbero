"""Entorno de prueba: datos temporales, clave maestra propia, servicio real, SQLite real y clientes HTTP separados."""
from __future__ import annotations

import shutil
import socket
import tempfile
import unittest
import warnings
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

warnings.filterwarnings("ignore", message=r"Using `httpx` with `starlette.testclient`")

from fastapi.testclient import TestClient  # noqa: E402

from cerbero_pf.config import Config, SmtpConfig  # noqa: E402
from cerbero_pf.crypto import generate_master_key_file  # noqa: E402
from cerbero_pf.service import Service  # noqa: E402
from cerbero_pf.web import COOKIE, create_app  # noqa: E402

PASSWORDS = {"propietario": "propietario-clave-1", "lector": "lector-clave-0001", "tercero": "tercero-clave-001"}
TEXT = "Contrato sintético de prueba: entrega 2, importe 0,00. Línea con acentos: ñ, á, ü.\n".encode("utf-8")
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
       b"\x00\x00\x00\rIDATx\x9cc\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class Clock:
    def __init__(self):
        self.moment = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        self.moment += timedelta(microseconds=1)
        return self.moment

    def advance(self, **delta) -> None:
        self.moment += timedelta(**delta)


class Env:
    def __init__(self, root: Path, clock: Clock | None = None, sender=None, new_key: bool = True, **overrides):
        self.root, self.clock, self.sender, self.overrides = root, clock, sender, overrides
        settings = {"allowed_hosts": ("testserver",), "export_roots": (root / "nas",),
                    "export_output_dir": root / "exports", "open_attempts_per_minute": 10_000, **overrides}
        self.cfg = Config(data_dir=root / "data", master_key_file=root / "secrets" / "master.key", **settings).validate()
        if new_key:
            generate_master_key_file(self.cfg.master_key_file)
        kwargs = {"sender": sender} if sender is not None else {}
        self.service = Service(self.cfg, now=clock, **kwargs) if clock else Service(self.cfg, **kwargs)
        self.app = create_app(self.service, start_worker=False)

    def restart(self, **overrides) -> "Env":
        """Servicio y aplicación nuevos sobre los mismos datos: equivale a reiniciar el proceso."""
        return Env(self.root, self.clock, self.sender, new_key=False, **{**self.overrides, **overrides})

    def create_users(self) -> None:
        self.service.create_user("propietario", PASSWORDS["propietario"], "Propietaria", "propietario@demo.invalid")
        self.service.create_user("lector", PASSWORDS["lector"], "Lector")
        self.service.create_user("tercero", PASSWORDS["tercero"], "Tercero")

    def client(self, username: str | None = None, ip: str = "127.0.0.1", cookie: str | None = None) -> TestClient:
        client = TestClient(self.app, client=(ip, 50000))
        if cookie:
            client.cookies.set(COOKIE, cookie)
            client.headers["X-CSRF-Token"] = client.get("/api/me").json()["csrf_token"]
        elif username:
            response = client.post("/api/login", json={"username": username, "password": PASSWORDS[username]})
            assert response.status_code == 200, response.text
            client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
        return client


class ServiceCase(unittest.TestCase):
    overrides: dict = {}
    use_clock = False

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cerbero-pf-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "nas").mkdir()
        self.clock = Clock() if self.use_clock else None
        self.env = self.make_env()
        self.env.create_users()
        self.owner = self.env.client("propietario")

    def make_env(self, **extra) -> Env:
        return Env(self.tmp, self.clock, **{**self.overrides, **extra})

    def export(self, data: bytes = TEXT, name: str = "Contrato.txt", client=None) -> tuple[dict, bytes]:
        client = client or self.owner
        response = client.post("/api/documents", content=data, headers={"X-Filename": name})
        self.assertEqual(response.status_code, 201, response.text)
        doc = response.json()["document"]
        return doc, client.get(response.json()["container_url"]).content

    def grant(self, doc_id: str, username: str = "lector") -> None:
        self.assertEqual(self.owner.post(f"/api/documents/{doc_id}/grants", json={"username": username}).status_code, 200)

    def mark(self, doc_id: str, state: str = "lost") -> dict:
        response = self.owner.post(f"/api/documents/{doc_id}/state", json={"state": state, "confirm_doc_id": doc_id})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["document"]

    def events(self, client=None) -> list[dict]:
        return (client or self.owner).get("/api/events").json()["events"]

    def notifications(self) -> list[dict]:
        return self.owner.get("/api/notifications").json()["notifications"]


def with_smtp(port: int, **extra) -> SmtpConfig:
    return replace(SmtpConfig(), enabled=True, host="127.0.0.1", port=port, retry_base_seconds=0, timeout_seconds=3,
                   **extra)
