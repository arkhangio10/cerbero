"""Permisos, revocación, persistencia, concurrencia y auditoría obligatoria, mediante llamadas directas a la API."""
from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import sqlite3
import threading
import time
import unittest

import support
from cerbero_pf import crypto
from cerbero_pf.service import RequestContext
from cerbero_pf.web import COOKIE


class ExportAndRecovery(support.ServiceCase):
    def test_path_export_keeps_original_and_reader_recovers_exact_bytes(self):
        original = self.tmp / "nas" / "Contrato.txt"
        original.write_bytes(support.TEXT)
        before = (hashlib.sha256(original.read_bytes()).hexdigest(), original.stat().st_mtime_ns, original.stat().st_size)
        doc, out = self.env.service.export_path("propietario", original)
        after = (hashlib.sha256(original.read_bytes()).hexdigest(), original.stat().st_mtime_ns, original.stat().st_size)
        self.assertEqual(before, after)
        self.assertEqual(out.parent, (self.tmp / "exports").resolve())
        self.grant(doc["id"])
        response = self.env.client("lector").post("/api/open", content=out.read_bytes())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(base64.b64decode(response.json()["content_b64"]), support.TEXT)

    def test_binary_image_roundtrip_is_exact(self):
        doc, container = self.export(support.PNG, "foto.png")
        self.assertEqual(doc["media_type"], "image/png")
        self.grant(doc["id"])
        body = self.env.client("lector").post("/api/open", content=container).json()
        self.assertEqual(base64.b64decode(body["content_b64"]), support.PNG)
        self.assertEqual(body["document"]["media_type"], "image/png")

    def test_two_exports_of_the_same_file_are_independent(self):
        first, c1 = self.export()
        second, c2 = self.export()
        self.assertNotEqual(first["id"], second["id"])
        self.assertNotEqual(c1, c2)
        conn = self.env.service.connect()
        rows = {r["id"]: r for r in conn.execute("SELECT * FROM documents").fetchall()}
        conn.close()
        keys = [crypto.unwrap_key(self.env.service.master_key, d, rows[d]["wrap_nonce"], rows[d]["wrapped_key"])
                for d in (first["id"], second["id"])]
        self.assertNotEqual(keys[0], keys[1])

    def test_no_key_material_reaches_the_container_or_the_reader(self):
        doc, container = self.export()
        self.grant(doc["id"])
        reader = self.env.client("lector")
        conn = self.env.service.connect()
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc["id"],)).fetchone()
        conn.close()
        doc_key = crypto.unwrap_key(self.env.service.master_key, doc["id"], row["wrap_nonce"], row["wrapped_key"])
        secrets_ = [doc_key, self.env.service.master_key, row["wrapped_key"]]
        exposed = [container, reader.post("/api/open", content=container).content, reader.get("/api/me").content,
                   self.owner.get("/api/documents").content, self.owner.get(f"/api/documents/{doc['id']}/audit").content]
        for blob in exposed:
            for secret in secrets_:
                for form in (secret, secret.hex().encode(), base64.b64encode(secret),
                             base64.urlsafe_b64encode(secret).rstrip(b"=")):
                    self.assertNotIn(form, blob)

    def test_tampered_or_substituted_containers_release_nothing(self):
        doc, container = self.export()
        other, _ = self.export(b"Otro documento sintetico\n", "Otro.txt")
        self.grant(doc["id"])
        reader = self.env.client("lector")
        _, _, hlen = crypto.PREFIX.unpack_from(container)
        end = crypto.PREFIX.size + hlen
        header = json.loads(container[crypto.PREFIX.size:end])
        swapped = json.dumps({**header, "doc": other["id"]}, sort_keys=True, separators=(",", ":")).encode()
        dated = json.dumps({**header, "created": "2020-01-01T00:00:00Z"}, sort_keys=True, separators=(",", ":")).encode()
        flipped = bytearray(container)
        flipped[-20] ^= 0x40
        cases = {
            "contenido alterado": bytes(flipped),
            "cabecera autenticada alterada": crypto.PREFIX.pack(crypto.MAGIC, 1, len(dated)) + dated + container[end:],
            "identidad sustituida": crypto.PREFIX.pack(crypto.MAGIC, 1, len(swapped)) + swapped + container[end:],
            "truncado": container[:-10],
        }
        for label, data in cases.items():
            with self.subTest(label):
                response = reader.post("/api/open", content=data)
                self.assertEqual(response.status_code, 422, response.text)
                self.assertNotIn("content_b64", response.json())
                self.assertNotIn(b"Contrato sint", response.content)
        self.assertFalse([e for e in self.events() if e["kind"] == "container_invalid"],
                         "un contenedor no validado no crea eventos atribuidos al documento")
        telemetry = self.owner.get("/api/telemetry").json()["events"]
        self.assertTrue(telemetry and all(not e["verified"] for e in telemetry))
        self.assertEqual(self.notifications(), [], "la telemetría no verificada no genera avisos")


class Permissions(support.ServiceCase):
    def setUp(self):
        super().setUp()
        self.doc, self.container = self.export()
        self.grant(self.doc["id"])
        self.third = self.env.client("tercero")
        self.reader = self.env.client("lector")

    def test_third_party_with_the_id_and_the_file_cannot_read_change_or_watch(self):
        doc_id = self.doc["id"]
        third = self.third
        self.assertEqual(third.post("/api/open", content=self.container).status_code, 403)
        self.assertEqual(third.get(f"/api/documents/{doc_id}").status_code, 404)
        self.assertEqual(third.get(f"/api/documents/{doc_id}/container").status_code, 404)
        self.assertEqual(third.get(f"/api/documents/{doc_id}/audit").status_code, 404)
        self.assertEqual(third.get(f"/api/events?doc_id={doc_id}").status_code, 404)
        self.assertEqual(third.post(f"/api/documents/{doc_id}/grants", json={"username": "tercero"}).status_code, 404)
        self.assertEqual(third.post(f"/api/documents/{doc_id}/grants/revoke", json={"username": "lector"}).status_code, 404)
        self.assertEqual(third.post(f"/api/documents/{doc_id}/state",
                                    json={"state": "revoked", "confirm_doc_id": doc_id}).status_code, 404)
        self.assertEqual(third.get("/api/events").json()["events"], [])
        self.assertEqual(third.get("/api/notifications").json()["notifications"], [])
        self.assertEqual(third.get("/api/documents").json()["documents"], [])
        note_id = self.notifications()[0]["id"]
        self.assertEqual(third.post(f"/api/notifications/{note_id}/read").status_code, 404)
        current = self.owner.get(f"/api/documents/{doc_id}").json()["document"]
        self.assertEqual(current["state"], "active")
        self.assertEqual([g["username"] for g in current["grants"] if not g["revoked_at"]], ["lector"])
        denied = [e for e in self.events() if e["kind"] == "access_denied"]
        self.assertEqual(denied[0]["actor_label"], "tercero")
        self.assertEqual(denied[0]["reason"], "no_permission")

    def test_reader_can_read_but_not_manage(self):
        doc_id = self.doc["id"]
        self.assertEqual(self.reader.post("/api/open", content=self.container).status_code, 200)
        self.assertEqual(self.reader.post(f"/api/documents/{doc_id}/grants", json={"username": "tercero"}).status_code, 404)
        self.assertEqual(self.reader.post(f"/api/documents/{doc_id}/state",
                                          json={"state": "lost", "confirm_doc_id": doc_id}).status_code, 404)
        self.assertEqual(self.reader.get("/api/events").json()["events"], [])

    def test_anonymous_request_is_recorded_and_requires_authentication(self):
        response = self.env.client().post("/api/open", content=self.container)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["result"], "auth_required")
        self.assertNotIn("content_b64", response.json())
        self.assertEqual(self.events()[0]["kind"], "access_request")
        self.assertEqual(self.events()[0]["actor_label"], "sin sesión")

    def test_unauthenticated_api_calls_are_refused(self):
        anon = self.env.client()
        for path in ("/api/me", "/api/documents", f"/api/documents/{self.doc['id']}", "/api/events",
                     "/api/notifications", "/api/telemetry"):
            with self.subTest(path):
                self.assertEqual(anon.get(path).status_code, 401)
        self.assertEqual(anon.post("/api/documents", content=b"x", headers={"X-Filename": "a.txt"}).status_code, 401)

    def test_state_changes_need_csrf_origin_and_confirmation(self):
        doc_id = self.doc["id"]
        body = {"state": "lost", "confirm_doc_id": doc_id}
        no_token = self.env.client(cookie=self.owner.cookies.get(COOKIE))
        no_token.headers.pop("X-CSRF-Token")
        self.assertEqual(no_token.post(f"/api/documents/{doc_id}/state", json=body).status_code, 403)
        self.assertEqual(no_token.post(f"/api/documents/{doc_id}/state", json=body,
                                       headers={"X-CSRF-Token": "falso"}).status_code, 403)
        self.assertEqual(self.owner.post(f"/api/documents/{doc_id}/state", json=body,
                                         headers={"Origin": "http://evil.example"}).status_code, 403)
        self.assertEqual(self.owner.post(f"/api/documents/{doc_id}/state",
                                         json={"state": "lost", "confirm_doc_id": "otro"}).status_code, 400)
        self.assertEqual(self.owner.post(f"/api/documents/{doc_id}/state",
                                         json={"state": "active", "confirm_doc_id": doc_id}).status_code, 400)
        self.assertEqual(self.owner.get(f"/api/documents/{doc_id}").json()["document"]["state"], "active")
        reader_cookie_only = self.env.client(cookie=self.reader.cookies.get(COOKIE))
        reader_cookie_only.headers.pop("X-CSRF-Token")
        self.assertEqual(reader_cookie_only.post("/api/open", content=self.container).status_code, 403)

    def test_grant_revocation_blocks_the_reader(self):
        self.assertEqual(self.reader.post("/api/open", content=self.container).status_code, 200)
        self.assertEqual(self.owner.post(f"/api/documents/{self.doc['id']}/grants/revoke",
                                         json={"username": "lector"}).status_code, 200)
        response = self.reader.post("/api/open", content=self.container)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["reason"], "grant_revoked")
        self.assertIn("lector", self.notifications()[0]["body"])


class Revocation(support.ServiceCase):
    def test_persisted_revocation_blocks_old_sessions_and_copies_even_after_restart(self):
        doc, container = self.export()
        self.grant(doc["id"])
        reader = self.env.client("lector")
        self.assertEqual(reader.post("/api/open", content=container).status_code, 200)
        copy_path = self.tmp / "copia.cerbero"
        copy_path.write_bytes(container)
        marked = self.mark(doc["id"])
        self.assertEqual(marked["state"], "lost")
        self.assertTrue(marked["effective_at"])
        for data in (container, copy_path.read_bytes()):
            response = reader.post("/api/open", content=data)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["reason"], "document_lost")
            self.assertNotIn("content_b64", response.json())
        self.assertEqual(self.owner.post("/api/open", content=container).status_code, 403)
        events_before = self.events()

        restarted = self.env.restart()
        old_session = restarted.client(cookie=reader.cookies.get(COOKIE))
        response = old_session.post("/api/open", content=copy_path.read_bytes())
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("content_b64", response.json())
        owner = restarted.client(cookie=self.owner.cookies.get(COOKIE))
        self.assertEqual(owner.get(f"/api/documents/{doc['id']}").json()["document"]["state"], "lost")
        events_after = owner.get("/api/events").json()["events"]
        self.assertEqual([e["id"] for e in events_after[1:]], [e["id"] for e in events_before])
        self.assertTrue(owner.get("/api/notifications").json()["notifications"])

        revoked = owner.post(f"/api/documents/{doc['id']}/state", json={"state": "revoked", "confirm_doc_id": doc["id"]})
        self.assertEqual(revoked.status_code, 200)
        self.assertEqual(old_session.post("/api/open", content=container).json()["reason"], "document_revoked")
        self.assertEqual(owner.post(f"/api/documents/{doc['id']}/state",
                                    json={"state": "lost", "confirm_doc_id": doc["id"]}).status_code, 409)

    def test_concurrent_opens_never_serve_after_the_revocation_commits(self):
        doc, container = self.export()
        self.grant(doc["id"])
        service = self.env.service
        _, reader = service.login("lector", support.PASSWORDS["lector"], "127.0.0.1")
        _, owner = service.login("propietario", support.PASSWORDS["propietario"], "127.0.0.1")
        results, stop = [], threading.Event()

        def worker():
            while not stop.is_set():
                outcome = service.open_container(container, reader, RequestContext(ip="127.0.0.1"))
                results.append((outcome.result, outcome.event_id))

        threads = [threading.Thread(target=worker) for _ in range(6)]
        for thread in threads:
            thread.start()
        time.sleep(0.4)
        revocation = service.set_state(owner, doc["id"], "lost", doc["id"], RequestContext(ip="127.0.0.1"))
        after = service.open_container(container, reader, RequestContext(ip="127.0.0.1"))
        time.sleep(0.3)
        stop.set()
        for thread in threads:
            thread.join()
        served = [eid for result, eid in results if result == "allowed"]
        self.assertTrue(served, "la prueba necesita aperturas concurrentes antes de revocar")
        self.assertTrue(all(eid < revocation["event_id"] for eid in served))
        self.assertEqual(after.result, "denied")
        self.assertTrue(any(result == "denied" for result, _ in results))
        self.assertEqual({r for r, _ in results}, {"allowed", "denied"})

    def test_no_content_when_the_audit_record_cannot_be_written(self):
        doc, container = self.export()
        self.grant(doc["id"])
        reader = self.env.client("lector")
        conn = sqlite3.connect(self.env.cfg.db_path)
        conn.execute("CREATE TRIGGER block_audit BEFORE INSERT ON events WHEN NEW.kind = 'content_served' "
                     "BEGIN SELECT RAISE(ABORT, 'disco lleno simulado'); END")
        conn.commit()
        conn.close()
        response = reader.post("/api/open", content=container)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("content_b64", response.json())
        self.assertNotIn(b"Contrato sint", response.content)
        self.assertFalse([e for e in self.events() if e["kind"] == "content_served"])


class SessionsAndLogin(support.ServiceCase):
    use_clock = True

    def test_session_expires_and_logout_ends_it(self):
        reader = self.env.client("lector")
        self.assertEqual(reader.get("/api/me").status_code, 200)
        self.clock.advance(hours=9)
        self.assertEqual(reader.get("/api/me").status_code, 401)
        owner = self.env.client("propietario")
        old = owner.cookies.get(COOKIE)
        self.assertEqual(owner.post("/api/logout").status_code, 200)
        reuse = self.env.client()
        reuse.cookies.set(COOKIE, old)
        self.assertEqual(reuse.get("/api/me").status_code, 401)

    def test_login_lockout_is_persistent_and_temporary(self):
        anon = self.env.client(ip="127.0.0.1")
        for _ in range(5):
            self.assertEqual(anon.post("/api/login", json={"username": "lector", "password": "incorrecta"}).status_code, 401)
        good = {"username": "lector", "password": support.PASSWORDS["lector"]}
        self.assertEqual(anon.post("/api/login", json=good).status_code, 429)
        restarted = self.env.restart()
        self.assertEqual(restarted.client().post("/api/login", json=good).status_code, 429)
        self.clock.advance(minutes=16)
        self.assertEqual(restarted.client().post("/api/login", json=good).status_code, 200)

    def test_unknown_user_and_wrong_password_look_the_same(self):
        anon = self.env.client()
        a = anon.post("/api/login", json={"username": "nadie", "password": "x" * 12}).json()
        b = anon.post("/api/login", json={"username": "lector", "password": "x" * 12}).json()
        self.assertEqual(a, b)


class OpenRateLimit(support.ServiceCase):
    overrides = {"open_attempts_per_minute": 3}

    def test_open_attempts_are_rate_limited(self):
        anon = self.env.client()
        codes = [anon.post("/api/open", content=b"basura").status_code for _ in range(4)]
        self.assertEqual(codes, [422, 422, 422, 429])



class ReviewRegressions(support.ServiceCase):
    """Hallazgos de la revisión adversarial del 12-nov-2026."""

    def test_concurrent_wrong_passwords_cannot_exceed_the_lockout(self):
        outcomes, lock = [], threading.Lock()

        def attempt():
            try:
                self.env.service.login("lector", "incorrecta-larga", "127.0.0.1")
            except Exception as exc:  # ServiceError con código 401 o 429
                with lock:
                    outcomes.append(getattr(exc, "status", None))

        threads = [threading.Thread(target=attempt) for _ in range(30)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(outcomes.count(401), 5)
        self.assertEqual(outcomes.count(429), 25)

    def test_concurrent_opens_cannot_exceed_the_rate_limit(self):
        env = self.env.restart(open_attempts_per_minute=3)
        results = []
        threads = [threading.Thread(target=lambda: results.append(
            env.service.open_container(b"basura", None, RequestContext(ip="127.0.0.1")).result)) for _ in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(results.count("invalid"), 3)
        self.assertEqual(results.count("rate_limited"), 17)

    def test_owner_can_mark_lost_locally_when_web_login_is_blocked(self):
        from cerbero_pf import demo
        from cerbero_pf.__main__ import main

        doc, container = self.export()
        self.grant(doc["id"])
        reader = self.env.client("lector")
        anon = self.env.client()
        for _ in range(5):
            anon.post("/api/login", json={"username": "propietario", "password": "incorrecta"})
        self.assertEqual(anon.post("/api/login", json={"username": "propietario",
                                                       "password": support.PASSWORDS["propietario"]}).status_code, 429)
        config = self.tmp / "config.toml"
        demo._write_config(config, support.free_port(), None)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["set-state", "--config", str(config), "--owner", "propietario", doc["id"], "lost"]), 0)
            self.assertEqual(main(["set-state", "--config", str(config), "--owner", "tercero", doc["id"], "revoked"]), 1)
        self.assertEqual(reader.post("/api/open", content=container).json()["reason"], "document_lost")

    def test_identifiers_with_a_trailing_newline_are_rejected(self):
        from cerbero_pf.service import ServiceError

        with self.assertRaises(ServiceError):
            self.env.service.create_user("alice\n", "contraseña-larga-1")
        self.assertEqual(self.owner.get(f"/api/documents/{crypto.new_doc_id()}%0A").status_code, 404)
        with self.assertRaises(ValueError):
            crypto.encrypt_container(b"x", crypto.new_doc_id() + "\n", "2026-11-12T12:00:00Z", 1024)


if __name__ == "__main__":
    unittest.main()
