"""Nombres maliciosos, cargas excesivas, archivos inválidos, formatos activos, rutas fuera del área y cabeceras."""
from __future__ import annotations

import os
import re
import shutil
import tempfile
import unittest
import urllib.parse
from pathlib import Path

import support
from cerbero_pf.config import STATIC_DIR, Config, ConfigError, load_config
from cerbero_pf.security import ACTIVE_MEDIA, OTHER_MEDIA, clean_text, display_name
from cerbero_pf.service import ServiceError

PROJECT = Path(__file__).resolve().parents[1]


def tree(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*")}


class MaliciousNames(support.ServiceCase):
    NAMES = ["../../../../Windows/win.ini", "..\\..\\evil.txt", "<script>alert(1)</script>.txt",
             "factura\u202etxt.exe", "linea1\r\nX-Inyectada: si.txt", "nul\x00byte.txt", "CON.txt",
             "a" * 500 + ".txt", "  ...  ", "C:\\Users\\otro\\secreto.txt", "/etc/passwd"]

    def test_names_are_neutralized_and_files_stay_in_the_data_area(self):
        before = tree(self.tmp)
        for raw in self.NAMES:
            with self.subTest(raw=raw[:30]):
                doc, _ = self.export(b"texto sintetico\n", urllib.parse.quote(raw, safe=""))
                name = doc["display_name"]
                self.assertFalse(set(name) & set('/\\<>:"|?*'))
                self.assertFalse(any(ord(ch) < 32 or ch in "\u202e\u200f" for ch in name))
                self.assertLessEqual(len(name), 120)
                self.assertTrue(doc["container_name"].endswith(".cerbero"))
                self.assertNotEqual(name.split(".")[0].lower(), "con")
        created = tree(self.tmp) - before
        allowed = re.compile(r"^data/(containers/pf_[A-Za-z0-9_-]{24}\.cerbero|cerbero_pf\.sqlite3(-wal|-shm)?)$")
        self.assertTrue(created and all(allowed.match(p) for p in created), created)

    def test_text_cleaning_for_logs(self):
        self.assertEqual(clean_text("a\r\nb\u202ec\x1b[31m", 50), "a bc[31m")
        self.assertEqual(display_name(""), "documento")
        agent = "UA\u202e malicioso".encode("utf-8")
        self.env.client("tercero").post("/api/open", content=b"x", headers={"User-Agent": agent})
        conn = self.env.service.connect()
        agents = [r[0] for r in conn.execute("SELECT user_agent FROM events").fetchall()]
        conn.close()
        self.assertTrue(agents and all("\u202e" not in a for a in agents))

    def test_frontend_never_injects_html(self):
        for script in STATIC_DIR.glob("*.js"):
            text = script.read_text(encoding="utf-8")
            for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
                self.assertNotIn(sink, text, f"{script.name} usa {sink}")
        for page in STATIC_DIR.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"<script>(?!</script>)", f"{page.name} tiene script en línea")
            self.assertNotIn("style=", text)


class Limits(support.ServiceCase):
    overrides = {"max_plaintext_bytes": 1024}

    def test_oversized_exports_are_refused_with_or_without_length(self):
        big = b"a" * 1025
        self.assertEqual(self.owner.post("/api/documents", content=big, headers={"X-Filename": "a.txt"}).status_code, 413)
        chunks = (b"a" * 256 for _ in range(5))
        self.assertEqual(self.owner.post("/api/documents", content=chunks, headers={"X-Filename": "a.txt"}).status_code, 413)
        self.assertEqual(self.owner.post("/api/documents", content=b"", headers={"X-Filename": "a.txt"}).status_code, 400)
        self.assertEqual(self.owner.get("/api/documents").json()["documents"], [])

    def test_oversized_open_requests_are_refused(self):
        self.assertEqual(self.env.client("tercero").post("/api/open", content=b"x" * 5000).status_code, 413)

    def test_invalid_files_are_rejected_and_logged_as_unverified(self):
        doc, container = self.export(b"hola\n")
        third = self.env.client("tercero")
        for label, data in {"vacío": b"", "aleatorio": os.urandom(300), "truncado": container[:30],
                            "imagen": support.PNG}.items():
            with self.subTest(label):
                response = third.post("/api/open", content=data)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["result"], "invalid")
        conn = self.env.service.connect()
        kinds = {r[0] for r in conn.execute("SELECT kind FROM events WHERE verified = 0").fetchall()}
        conn.close()
        self.assertEqual(kinds, {"container_invalid"})


class ActiveFormats(support.ServiceCase):
    SAMPLES = {
        "pagina.html": b"<html><script>fetch('/api/documents')</script></html>",
        "dibujo.svg": b"<svg xmlns='http://www.w3.org/2000/svg' onload='alert(1)'/>",
        "notas.txt": b"  <svg onload=alert(1)>",
        "foto.png": b"<!DOCTYPE html><img src=x onerror=alert(1)>",
        "macro.docm": b"PK\x03\x04 macro",
        "script.js": b"alert(1)",
        "informe.pdf": b"%PDF-1.7 sintetico",
    }

    def test_active_and_unknown_formats_are_never_served(self):
        reader = self.env.client("lector")
        for name, data in self.SAMPLES.items():
            with self.subTest(name):
                doc, container = self.export(data, name)
                self.assertIn(doc["media_type"], (ACTIVE_MEDIA, OTHER_MEDIA))
                self.grant(doc["id"])
                response = reader.post("/api/open", content=container)
                self.assertEqual(response.status_code, 415)
                self.assertEqual(response.headers["content-type"], "application/json")
                self.assertNotIn("content_b64", response.json())
                self.assertNotIn(data[:12], response.content)

    def test_text_with_markup_in_the_middle_is_served_as_plain_text(self):
        doc, container = self.export(b"Nota: <b>no es HTML</b> aqui.\n", "nota.txt")
        self.grant(doc["id"])
        body = self.env.client("lector").post("/api/open", content=container).json()
        self.assertEqual(body["document"]["media_type"], "text/plain; charset=utf-8")


class PathExport(support.ServiceCase):
    def setUp(self):
        super().setUp()
        self.inside = self.tmp / "nas" / "ok.txt"
        self.inside.write_bytes(b"dentro\n")
        self.outside = self.tmp / "fuera.txt"
        self.outside.write_bytes(b"fuera\n")

    def expect(self, path, code):
        with self.assertRaises(ServiceError) as caught:
            self.env.service.export_path("propietario", path)
        self.assertEqual(caught.exception.code, code)

    def test_paths_outside_the_authorized_area_are_refused(self):
        self.expect(self.outside, "outside_roots")
        self.expect(self.tmp / "nas" / ".." / "fuera.txt", "outside_roots")
        self.expect(self.tmp / "nas", "not_regular")
        self.expect(self.tmp / "nas" / "no-existe.txt", "not_found")
        doc, out = self.env.service.export_path("propietario", self.inside)
        self.assertTrue(out.is_file())
        self.assertEqual(self.inside.read_bytes(), b"dentro\n")

    def test_links_escaping_the_area_are_refused(self):
        link = self.tmp / "nas" / "enlace.txt"
        try:
            os.symlink(self.outside, link)
        except OSError as exc:
            self.skipTest(f"este Windows no permite crear enlaces simbólicos sin privilegios: {exc}")
        self.expect(link, "outside_roots")

    @unittest.skipUnless(os.name == "nt", "las junctions son de Windows")
    def test_directory_junction_escaping_the_area_is_refused(self):
        import _winapi

        secret_dir = self.tmp / "privado"
        secret_dir.mkdir()
        (secret_dir / "secreto.txt").write_bytes(b"no exportar\n")
        _winapi.CreateJunction(str(secret_dir), str(self.tmp / "nas" / "atajo"))
        self.expect(self.tmp / "nas" / "atajo" / "secreto.txt", "outside_roots")


class HeadersAndHosts(support.ServiceCase):
    def test_security_headers_on_pages_and_api(self):
        anon = self.env.client()
        for path in ("/panel", "/visor", "/api/health", "/static/app.css"):
            with self.subTest(path):
                response = anon.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn("default-src 'none'", response.headers["content-security-policy"])
                self.assertIn("frame-ancestors 'none'", response.headers["content-security-policy"])
                self.assertEqual(response.headers["x-content-type-options"], "nosniff")
                self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertEqual(anon.get("/api/health").headers["cache-control"], "no-store")

    def test_unknown_host_and_static_traversal_are_refused(self):
        anon = self.env.client()
        self.assertEqual(anon.get("/api/health", headers={"Host": "evil.example"}).status_code, 400)
        for path in ("/static/../service.py", "/static/%2e%2e/service.py", "/static/..%5cservice.py"):
            with self.subTest(path):
                response = anon.get(path)
                self.assertIn(response.status_code, (400, 404))
                self.assertNotIn(b"open_container", response.content)


class Configuration(unittest.TestCase):
    def test_example_config_loads_and_unsafe_settings_are_refused(self):
        cfg = load_config(PROJECT / "config.example.toml")
        self.assertEqual(cfg.host, "127.0.0.1")
        self.assertFalse(cfg.smtp.enabled)
        self.assertEqual(cfg.geo_provider, "none")
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with self.assertRaises(ConfigError):
            Config(data_dir=root / "d", master_key_file=root / "k", host="0.0.0.0").validate()
        Config(data_dir=root / "d", master_key_file=root / "k", host="::1").validate()
        with self.assertRaises(ConfigError):
            Config(data_dir=root / "d", master_key_file=root / "k", geo_provider="externo").validate()
        with self.assertRaises(ConfigError):
            Config(data_dir=root / "d", master_key_file=root / "k", max_plaintext_bytes=64 * 1024 * 1024).validate()

    def test_repository_has_no_secrets_or_runtime_data(self):
        for path in PROJECT.rglob("*"):
            if ".venv" in path.parts or "__pycache__" in path.parts or not path.is_file():
                continue
            self.assertNotIn(path.suffix, (".key", ".sqlite3", ".eml", ".cerbero"), path)
            if path.suffix in (".py", ".toml", ".md", ".txt", ".js", ".html", ".css"):
                self.assertNotRegex(path.read_text(encoding="utf-8"), r"cerbero-pf-master-v1:[A-Za-z0-9+/]{43}=", path)



class ReviewRegressions(support.ServiceCase):
    def test_small_json_endpoints_refuse_large_or_unsized_bodies_before_authentication(self):
        anon = self.env.client()
        big = b"{" + b" " * (20 * 1024) + b"}"
        for path in ("/api/login", "/api/documents/pf_x/grants", "/api/documents/pf_x/state"):
            with self.subTest(path):
                response = anon.post(path, content=big, headers={"Content-Type": "application/json"})
                self.assertEqual(response.status_code, 413)
        chunked = anon.post("/api/login", content=(b"{}" for _ in range(1)), headers={"Content-Type": "application/json"})
        self.assertEqual(chunked.status_code, 411)

    def test_origin_matches_the_configured_public_url_behind_a_proxy(self):
        env = self.env.restart(public_base_url="https://nas.example")
        owner = env.client("propietario")
        doc, _ = self.export(client=owner)
        body = {"username": "lector"}
        ok = owner.post(f"/api/documents/{doc['id']}/grants", json=body, headers={"Origin": "https://nas.example"})
        self.assertEqual(ok.status_code, 200)
        evil = owner.post(f"/api/documents/{doc['id']}/grants/revoke", json=body, headers={"Origin": "https://evil.example"})
        self.assertEqual(evil.status_code, 403)


if __name__ == "__main__":
    unittest.main()
