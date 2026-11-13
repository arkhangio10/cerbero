"""Flujo completo con el servidor real en otro proceso, SQLite real, buzón SMTP local y navegador."""
from __future__ import annotations

import contextlib
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import support
from cerbero_pf import demo
from cerbero_pf.config import load_config
from cerbero_pf.crypto import generate_master_key_file
from cerbero_pf.service import Service

try:
    from playwright.sync_api import expect, sync_playwright
except ImportError:  # dependencia opcional sólo para esta prueba
    sync_playwright = None


class DemoFlow(unittest.TestCase):
    def test_demo_runs_end_to_end_against_the_real_server(self):
        root = Path(tempfile.mkdtemp(prefix="cerbero-pf-demo-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with contextlib.redirect_stdout(io.StringIO()):
            summary = demo.run_demo(root / "demo")
        self.assertTrue(summary["passed"], [c for c in summary["checks"] if not c["ok"]])
        self.assertEqual({c["step"] for c in summary["checks"]}, {"1", "2", "3", "4", "5", "6"})
        self.assertTrue((root / "demo" / "demo-transcript.txt").is_file())
        original = (root / "demo" / "nas" / "Contrato.txt").read_bytes()
        self.assertEqual(original, demo.SYNTHETIC_TEXT.encode())

    def test_existing_folders_without_the_demo_marker_are_never_deleted(self):
        root = Path(tempfile.mkdtemp(prefix="cerbero-pf-demo-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "importante.txt").write_text("no borrar", encoding="utf-8")
        with self.assertRaises(Exception):
            demo.run_demo(root, fresh=True)
        self.assertTrue((root / "importante.txt").is_file())


@unittest.skipIf(sync_playwright is None, "playwright no está instalado en este entorno")
class BrowserFlow(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="cerbero-pf-browser-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        for name in ("secrets", "data", "nas", "exports"):
            (self.root / name).mkdir()
        port = support.free_port()
        config = self.root / "config.toml"
        demo._write_config(config, port, None)
        cfg = load_config(config)
        generate_master_key_file(cfg.master_key_file)
        service = Service(cfg)
        for user, password in support.PASSWORDS.items():
            service.create_user(user, password, user.capitalize(), f"{user}@demo.invalid")
        self.server = demo._Server(config, self.root / "server.log", port)
        self.server.start()
        self.addCleanup(self.server.stop)
        self.base = self.server.base
        self.shots = os.environ.get("CERBERO_PF_SCREENSHOTS")

    def shot(self, page, name):
        if self.shots:
            Path(self.shots).mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(Path(self.shots) / f"{name}.png"), full_page=True)

    def login(self, page, user):
        page.fill("#login-user", user)
        page.fill("#login-pass", support.PASSWORDS[user])
        page.click("#login-form button[type=submit]")

    def open_file(self, page, path):
        page.set_input_files("#container", str(path))
        page.click("#open-form button[type=submit]")

    def test_viewer_and_panel_in_two_browser_sessions(self):
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch()
            except Exception as exc:  # navegador no instalado: se informa como omitida, no como aprobada
                self.skipTest(f"Chromium no disponible para Playwright: {exc}")
            try:
                self.flow(browser)
            finally:
                browser.close()

    def flow(self, browser):
        problems = []

        def watch(page):
            page.on("console", lambda m: problems.append(m.text)
                    if m.type == "error" and not m.text.startswith("Failed to load resource") else None)
            page.on("pageerror", lambda exc: problems.append(str(exc)))
            return page

        owner = watch(browser.new_context(accept_downloads=True).new_page())
        owner.goto(f"{self.base}/panel")
        self.login(owner, "propietario")
        expect(owner.locator("#app-view")).to_be_visible()
        source = self.root / "nas" / "Contrato.txt"
        source.write_bytes(support.TEXT)
        owner.set_input_files("#export-file", str(source))
        with owner.expect_download() as download:
            owner.click("#export-form button[type=submit]")
        container = self.root / "exports" / "Contrato.cerbero"
        download.value.save_as(container)
        self.assertEqual(download.value.suggested_filename, "Contrato.cerbero")
        expect(owner.locator("#export-msg")).to_contain_text("El archivo original no se modificó")
        expect(owner.locator(".doc .seal")).to_have_text("Activo")
        owner.fill(".doc input[type=text]", "lector")
        owner.click(".doc form button[type=submit]")
        expect(owner.locator(".grants")).to_contain_text("lector")

        reader = watch(browser.new_context().new_page())
        reader.goto(f"{self.base}/visor")
        expect(reader.locator(".notice")).to_contain_text("Cada acceso queda registrado")
        self.open_file(reader, container)
        expect(reader.locator("#status-title")).to_have_text("Autorización requerida")
        self.login(reader, "lector")
        expect(reader.locator("#status-title")).to_have_text("Acceso permitido")
        expect(reader.locator("#content pre")).to_contain_text("Contrato sintético de prueba")
        self.shot(reader, "visor-permitido")

        owner.click("#refresh")
        expect(owner.locator("#events")).to_contain_text("Contenido entregado al visor")
        expect(owner.locator("#events tr").first).to_contain_text("lector")
        owner.get_by_role("button", name="Marcar como extraviado", exact=True).click()
        owner.get_by_role("button", name="Confirmar: marcar como extraviado").click()
        expect(owner.locator(".doc .seal")).to_have_text("Extraviado")
        expect(owner.locator(".doc .message")).to_contain_text("Efectivo desde")

        copy = self.root / "copia.cerbero"
        shutil.copyfile(container, copy)
        third = watch(browser.new_context().new_page())
        third.goto(f"{self.base}/visor")
        self.open_file(third, copy)
        expect(third.locator("#status-title")).to_have_text("Documento extraviado")
        expect(third.locator("#content")).to_be_empty()

        self.open_file(reader, container)
        expect(reader.locator("#status-title")).to_have_text("Documento extraviado")
        expect(reader.locator("#content")).to_be_empty()
        self.shot(reader, "visor-extraviado")

        bad = self.root / "roto.cerbero"
        bad.write_bytes(os.urandom(200))
        self.open_file(third, bad)
        expect(third.locator("#status-title")).to_have_text("Archivo inválido")

        third.click("#location summary")
        third.click("#share-location")
        expect(third.locator("#location-msg")).to_contain_text("Permiso denegado")
        self.open_file(third, copy)
        expect(third.locator("#status-title")).to_have_text("Documento extraviado")

        located = watch(browser.new_context(geolocation={"latitude": -12.05, "longitude": -77.04, "accuracy": 25},
                                            permissions=["geolocation"]).new_page())
        located.goto(f"{self.base}/visor")
        located.click("#location summary")
        located.click("#share-location")
        expect(located.locator("#location-msg")).to_contain_text("-12.050")
        self.open_file(located, copy)
        expect(located.locator("#status-title")).to_have_text("Documento extraviado")

        owner.click("#refresh")
        expect(owner.locator("#alerts")).to_contain_text("Acceso denegado: Contrato.cerbero")
        expect(owner.locator("#alerts")).to_contain_text("Correo desactivado")
        expect(owner.locator("#events")).to_contain_text("permiso denegado por el navegador")
        expect(owner.locator("#events")).to_contain_text("declarada por el navegador: -12.050, -77.040")
        owner.click("#telemetry >> xpath=ancestor::details/summary")
        self.shot(owner, "panel-extraviado")

        self.server.stop()
        self.open_file(reader, container)
        expect(reader.locator("#status-title")).to_have_text("Servicio no disponible")
        self.assertEqual(problems, [], "errores de consola o violaciones de CSP")


if __name__ == "__main__":
    unittest.main()
