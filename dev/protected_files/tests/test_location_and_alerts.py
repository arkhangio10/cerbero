"""IP, proxies, ubicación aproximada y declarada; avisos, cola SMTP, reintentos, reinicios, duplicados y ráfagas."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import support
from cerbero_pf import crypto, geo
from cerbero_pf.config import Config, ConfigError, SmtpConfig
from cerbero_pf.mail import read_mailbox, start_mailbox

GEO_CSV = ("network,country,region,city,accuracy_radius_km\n"
           "1.1.1.0/24,ZZ,Región de prueba,Ciudad de prueba,100\n"
           "10.0.0.0/8,ZZ,Privada,No debe usarse,1\n")


class IpRules(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(geo.ip_class("127.0.0.1"), "loopback")
        self.assertEqual(geo.ip_class("::1"), "loopback")
        self.assertEqual(geo.ip_class("192.168.1.4"), "privada")
        self.assertEqual(geo.ip_class("169.254.3.3"), "enlace local")
        self.assertEqual(geo.ip_class("1.1.1.7"), "pública")
        self.assertEqual(geo.ip_class("testclient"), "inválida")

    def test_forwarded_header_needs_a_trusted_proxy(self):
        spoofed = geo.client_address("127.0.0.1", "1.1.1.7", ())
        self.assertEqual((spoofed.ip, spoofed.source), ("127.0.0.1", "conexión"))
        self.assertEqual(spoofed.forwarded_raw, "1.1.1.7")
        trusted = geo.client_address("127.0.0.1", "9.9.9.9, 1.1.1.7", ("127.0.0.1/32",))
        self.assertEqual(trusted.ip, "1.1.1.7")
        garbage = geo.client_address("127.0.0.1", "no-es-una-ip", ("127.0.0.1/32",))
        self.assertEqual(garbage.ip, "127.0.0.1")
        untrusted_peer = geo.client_address("203.0.113.9", "1.1.1.7", ("127.0.0.1/32",))
        self.assertEqual(untrusted_peer.ip, "203.0.113.9")

    def test_no_provider_and_private_addresses_never_invent_a_place(self):
        none = geo.NoGeo()
        for ip in ("127.0.0.1", "10.1.2.3", "1.1.1.7"):
            result = geo.locate(ip, none)
            self.assertEqual(result["status"], "unavailable")
            self.assertFalse({"city", "lat", "lon"} & set(result))
            self.assertEqual(geo.describe_location(result), "no disponible")

    def test_client_location_validation(self):
        self.assertEqual(geo.client_location(None, "t")["status"], "not_requested")
        self.assertEqual(geo.client_location('{"status":"denied"}', "t")["status"], "denied")
        for raw in ('{"status":"granted","lat":200,"lon":0,"accuracy_m":5}', '{"status":"granted","lat":"NaN"}',
                    "no-json", "{" + " " * 600 + "}", '{"status":"granted","lat":true,"lon":1,"accuracy_m":1}'):
            result = geo.client_location(raw, "t")
            self.assertEqual(result["status"], "invalid", raw[:30])
            self.assertNotIn("lat", result)
        ok = geo.client_location('{"status":"granted","lat":-12.05,"lon":-77.04,"accuracy_m":35,'
                                 '"timestamp_ms":1794480000000}', "t")
        self.assertEqual(ok["status"], "declared")
        self.assertIn("declarada por el cliente", ok["provenance"])
        self.assertEqual(ok["accuracy_m"], 35.0)
        self.assertTrue(ok["reported_at"].endswith("Z"))


class LocationInEvents(support.ServiceCase):
    def setUp(self):
        super().setUp()
        self.doc, self.container = self.export()
        self.grant(self.doc["id"])

    def last_event(self) -> dict:
        return self.events()[0]

    def test_spoofed_forwarded_header_is_recorded_but_ignored(self):
        reader = self.env.client("lector")
        reader.post("/api/open", content=self.container, headers={"X-Forwarded-For": "1.1.1.7"})
        event = self.last_event()
        self.assertEqual((event["ip"], event["ip_source"]), ("127.0.0.1", "conexión"))
        self.assertEqual(event["forwarded_header"], "1.1.1.7")
        self.assertEqual(event["geo"]["status"], "unavailable")
        self.assertEqual(event["geo_text"], "no disponible")

    def test_public_ip_without_provider_is_unavailable(self):
        self.env.client("lector", ip="1.1.1.7").post("/api/open", content=self.container)
        event = self.last_event()
        self.assertEqual(event["ip"], "1.1.1.7")
        self.assertEqual(event["geo"]["reason"], "sin proveedor geográfico")

    def test_denied_browser_location_is_recorded_and_changes_no_permission(self):
        header = {"X-Client-Location": json.dumps({"status": "denied"})}
        self.assertEqual(self.env.client("lector").post("/api/open", content=self.container, headers=header).status_code, 200)
        self.assertEqual(self.last_event()["client_location"]["status"], "denied")
        self.assertNotIn("lat", self.last_event()["client_location"])
        self.assertEqual(self.env.client("tercero").post("/api/open", content=self.container, headers=header).status_code, 403)
        self.assertEqual(self.last_event()["client_location"]["status"], "denied")

    def test_declared_location_is_stored_as_client_claim(self):
        loc = {"status": "granted", "lat": -12.0464, "lon": -77.0428, "accuracy_m": 30, "timestamp_ms": 1794480000000}
        self.env.client("lector").post("/api/open", content=self.container, headers={"X-Client-Location": json.dumps(loc)})
        recorded = self.last_event()["client_location"]
        self.assertEqual((recorded["status"], recorded["lat"], recorded["accuracy_m"]), ("declared", -12.0464, 30.0))
        self.assertIn("declarada por el cliente", recorded["provenance"])
        self.assertTrue(recorded["received_at"])


class TrustedProxyAndLocalBase(support.ServiceCase):
    def make_env(self, **extra):
        csv_path = self.tmp / "geo.csv"
        csv_path.write_text(GEO_CSV, encoding="utf-8")
        return super().make_env(trusted_proxies=("127.0.0.1/32",), geo_provider="csv", geo_csv_path=csv_path, **extra)

    def test_trusted_proxy_and_local_base_give_an_approximate_place(self):
        doc, container = self.export()
        self.env.client("tercero").post("/api/open", content=container, headers={"X-Forwarded-For": "1.1.1.7"})
        event = self.events()[0]
        self.assertEqual(event["ip"], "1.1.1.7")
        self.assertEqual(event["geo"]["status"], "approximate")
        self.assertIn("Ciudad de prueba", event["geo_text"])
        self.assertIn("puede reflejar una VPN", event["geo_text"])

    def test_private_and_unmatched_addresses_are_not_looked_up(self):
        doc, container = self.export()
        third = self.env.client("tercero")
        third.post("/api/open", content=container, headers={"X-Forwarded-For": "10.1.2.3"})
        self.assertEqual(self.events()[0]["geo"]["reason"], "IP privada")
        third.post("/api/open", content=container, headers={"X-Forwarded-For": "8.8.8.8"})
        self.assertEqual(self.events()[0]["geo"]["reason"], "sin resultado en la base local")


class SimulatedProvider(support.ServiceCase):
    overrides = {"geo_provider": "simulated"}

    def test_simulated_results_are_always_labelled(self):
        doc, container = self.export()
        self.mark(doc["id"])
        self.env.client("tercero").post("/api/open", content=container)
        self.assertTrue(self.events()[0]["geo_text"].startswith("SIMULADO"))
        self.assertIn("SIMULADO", self.notifications()[0]["body"])


class Notifications(support.ServiceCase):
    """Sin SMTP: avisos persistentes en el panel; correo marcado como desactivado."""

    def test_disabled_smtp_keeps_panel_notification(self):
        doc, container = self.export()
        self.mark(doc["id"])
        self.env.client("tercero").post("/api/open", content=container)
        note = self.notifications()[0]
        self.assertEqual(note["email_state"], "disabled")
        self.assertIsNone(note["email_status"])
        self.assertIn("Se intentó acceder a Contrato.cerbero, marcado como extraviado. Acceso denegado.", note["body"])
        self.assertIn("Ubicación aproximada por IP: no disponible", note["body"])

    def test_forged_id_does_not_create_an_incident(self):
        doc, container = self.export()
        forged, _ = crypto.encrypt_container(b"falso", doc["id"], "2026-11-12T12:00:00Z", 1024)
        response = self.env.client("tercero").post("/api/open", content=forged)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.notifications(), [])
        self.assertFalse([e for e in self.events() if e["kind"] != "export"])
        telemetry = self.owner.get("/api/telemetry").json()["events"]
        self.assertEqual(telemetry[0]["claimed_doc_id"], doc["id"])
        self.assertEqual(telemetry[0]["reason"], "does_not_match_registered_export")

    def test_owner_reading_own_events_after_mark_read(self):
        doc, container = self.export()
        self.mark(doc["id"])
        self.env.client("tercero").post("/api/open", content=container)
        note = self.notifications()[0]
        self.assertEqual(self.owner.post(f"/api/notifications/{note['id']}/read").status_code, 200)
        self.assertTrue(self.notifications()[0]["read_at"])


class MailCase(support.ServiceCase):
    use_clock = True
    smtp_extra: dict = {}

    def setUp(self):
        self.mail_dir = Path(tempfile.mkdtemp(prefix="cerbero-pf-mail-"))
        self.addCleanup(shutil.rmtree, self.mail_dir, ignore_errors=True)
        self.port = support.free_port()
        self.overrides = {"smtp": support.with_smtp(self.port, **self.smtp_extra)}
        super().setUp()
        self.doc, self.container = self.export()
        self.mark(self.doc["id"])

    def start_mailbox(self):
        controller = start_mailbox(self.mail_dir, "127.0.0.1", self.port)
        self.addCleanup(controller.stop)
        return controller

    def attempt(self, username="tercero", headers=None):
        client = self.env.client(username) if username else self.env.client()
        return client.post("/api/open", content=self.container, headers=headers or {})


class SmtpDelivery(MailCase):
    def test_message_reaches_local_mailbox_without_content_keys_or_coordinates(self):
        self.start_mailbox()
        loc = {"status": "granted", "lat": -12.0464321, "lon": -77.0428765, "accuracy_m": 12}
        self.assertEqual(self.attempt(headers={"X-Client-Location": json.dumps(loc)}).status_code, 403)
        self.assertEqual(self.notifications()[0]["email_status"], "pending")
        self.assertEqual(self.env.service.process_outbox(), {"sent": 1, "retry": 0, "failed": 0})
        note = self.notifications()[0]
        self.assertEqual((note["email_status"], note["email_attempts"]), ("sent", 1))
        messages = read_mailbox(self.mail_dir)
        self.assertEqual(len(messages), 1)
        message = messages[0][1]
        self.assertEqual(message["To"], "propietario@demo.invalid")
        body = message.get_content()
        self.assertIn("Ubicación aproximada por IP: no disponible", body)
        self.assertIn("/panel", body)
        for leaked in ("Contrato sint", "-12.04", "-77.04", "master", "BEGIN"):
            self.assertNotIn(leaked, body)
        self.assertFalse(message.is_multipart(), "sin adjuntos")


class SmtpFailure(MailCase):
    smtp_extra = {"max_attempts": 2}

    def test_failure_is_pending_then_failed_never_sent_and_access_stays_denied(self):
        self.assertEqual(self.attempt().status_code, 403)
        self.assertEqual(self.env.service.process_outbox(), {"sent": 0, "retry": 1, "failed": 0})
        note = self.notifications()[0]
        self.assertEqual(note["email_status"], "pending")
        self.assertTrue(note["email_error"])
        self.clock.advance(seconds=1)
        self.assertEqual(self.env.service.process_outbox(), {"sent": 0, "retry": 0, "failed": 1})
        note = self.notifications()[0]
        self.assertEqual((note["email_status"], note["email_attempts"]), ("failed", 2))
        self.assertIsNone(note["email_sent_at"])
        self.assertTrue([e for e in self.events() if e["kind"] == "access_denied"])
        self.assertEqual(self.attempt().status_code, 403)

    def test_queue_and_events_survive_restart_and_are_sent_later(self):
        self.attempt()
        self.env.service.process_outbox()
        restarted = self.env.restart()
        owner = restarted.client(cookie=self.owner.cookies.get("cerbero_pf_session"))
        self.assertEqual(owner.get("/api/notifications").json()["notifications"][0]["email_status"], "pending")
        self.start_mailbox()
        self.clock.advance(seconds=1)
        self.assertEqual(restarted.service.process_outbox()["sent"], 1)
        self.assertEqual(owner.get("/api/notifications").json()["notifications"][0]["email_status"], "sent")
        self.assertEqual(len(read_mailbox(self.mail_dir)), 1)
        self.assertTrue([e for e in owner.get("/api/events").json()["events"] if e["kind"] == "access_denied"])


class DuplicatesAndBursts(MailCase):
    smtp_extra = {"hourly_cap_per_owner": 2}

    def test_duplicates_are_grouped_with_their_count(self):
        third = self.env.client("tercero")
        for _ in range(5):
            self.assertEqual(third.post("/api/open", content=self.container).status_code, 403)
        notes = self.notifications()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["count"], 5)
        self.assertEqual(len([e for e in self.events() if e["kind"] == "access_denied"]), 5)
        self.clock.advance(minutes=16)
        third.post("/api/open", content=self.container)
        self.assertEqual(len(self.notifications()), 2)

    def test_bursts_beyond_the_hourly_cap_skip_email_but_keep_the_notice(self):
        self.attempt("tercero")
        self.attempt("lector")
        self.attempt(None)
        states = sorted(n["email_state"] for n in self.notifications())
        self.assertEqual(states, ["burst_skipped", "queued", "queued"])


class SmtpSafety(unittest.TestCase):
    def test_external_server_requires_explicit_opt_in(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        base = Config(data_dir=root / "d", master_key_file=root / "k" / "m.key")
        external = replace(SmtpConfig(), enabled=True, host="smtp.example.com")
        with self.assertRaises(ConfigError):
            replace(base, smtp=external).validate()
        replace(base, smtp=replace(external, allow_external=True)).validate()



class ReviewRegressions(support.ServiceCase):
    def test_absurd_numbers_in_browser_location_are_recorded_as_invalid(self):
        doc, container = self.export()
        raw = '{"status":"granted","lat":1,"lon":1,"accuracy_m":' + "9" * 400 + "}"
        response = self.env.client("tercero").post("/api/open", content=container, headers={"X-Client-Location": raw})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.events()[0]["client_location"]["status"], "invalid")

    def test_a_failed_quit_after_accepted_data_still_counts_as_sent(self):
        from unittest import mock
        import smtplib
        from cerbero_pf.mail import SmtpSender

        fake = mock.MagicMock()
        fake.send_message.return_value = {}
        fake.quit.side_effect = smtplib.SMTPServerDisconnected("cerrado")
        with mock.patch("cerbero_pf.mail.smtplib.SMTP", return_value=fake):
            SmtpSender(support.with_smtp(25)).send("a@demo.invalid", "asunto", "cuerpo")
        fake.close.assert_called_once()
        fake.send_message.return_value = {"a@demo.invalid": (550, b"no")}
        fake.quit.side_effect = None
        with mock.patch("cerbero_pf.mail.smtplib.SMTP", return_value=fake):
            with self.assertRaises(smtplib.SMTPRecipientsRefused):
                SmtpSender(support.with_smtp(25)).send("a@demo.invalid", "asunto", "cuerpo")


if __name__ == "__main__":
    unittest.main()
