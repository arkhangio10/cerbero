"""Formato del contenedor, AEAD, exportaciones independientes y clave maestra."""
from __future__ import annotations

import base64
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import support
from cerbero_pf import crypto
from cerbero_pf.config import Config

MAX = 1024 * 1024
CREATED = "2026-11-12T12:00:00Z"


def rebuild(header: dict, ciphertext: bytes, version: int = 1, raw: bytes | None = None) -> bytes:
    body = raw if raw is not None else json.dumps(header, sort_keys=True, separators=(",", ":")).encode()
    return crypto.PREFIX.pack(crypto.MAGIC, version, len(body)) + body + ciphertext


def split(container: bytes) -> tuple[dict, bytes]:
    _, _, length = crypto.PREFIX.unpack_from(container)
    end = crypto.PREFIX.size + length
    return json.loads(container[crypto.PREFIX.size:end]), container[end:]


class ContainerFormat(unittest.TestCase):
    def setUp(self):
        self.doc_id = crypto.new_doc_id()
        self.container, self.key = crypto.encrypt_container(support.TEXT, self.doc_id, CREATED, MAX)

    def test_roundtrip_returns_exact_bytes(self):
        parsed = crypto.parse_container(self.container, MAX)
        self.assertEqual(parsed.doc_id, self.doc_id)
        self.assertEqual(crypto.decrypt_container(parsed, self.key), support.TEXT)

    def test_each_export_uses_a_new_key_and_nonce(self):
        other_id = crypto.new_doc_id()
        other, other_key = crypto.encrypt_container(support.TEXT, other_id, CREATED, MAX)
        self.assertNotEqual(self.doc_id, other_id)
        self.assertNotEqual(self.key, other_key)
        self.assertNotEqual(split(self.container)[0]["nonce"], split(other)[0]["nonce"])
        with self.assertRaises(crypto.ContainerError):
            crypto.decrypt_container(crypto.parse_container(other, MAX), self.key)

    def test_container_carries_no_key_and_no_plaintext(self):
        for form in (self.key, self.key.hex().encode(), base64.b64encode(self.key), base64.urlsafe_b64encode(self.key)):
            self.assertNotIn(form, self.container)
        self.assertNotIn(support.TEXT[:20], self.container)

    def test_tampering_with_content_header_or_identity_fails_authentication(self):
        header, ciphertext = split(self.container)
        flipped = bytearray(ciphertext)
        flipped[3] ^= 0x01
        cases = {
            "contenido": rebuild(header, bytes(flipped)),
            "etiqueta": rebuild(header, ciphertext[:-1] + bytes([ciphertext[-1] ^ 1])),
            "identidad": rebuild({**header, "doc": crypto.new_doc_id()}, ciphertext),
            "fecha": rebuild({**header, "created": "2020-01-01T00:00:00Z"}, ciphertext),
        }
        for label, data in cases.items():
            with self.subTest(label):
                parsed = crypto.parse_container(data, MAX)
                with self.assertRaises(crypto.ContainerError) as caught:
                    crypto.decrypt_container(parsed, self.key)
                self.assertEqual(caught.exception.code, "auth_failed")

    def test_strict_format_rejects_malformed_containers(self):
        header, ciphertext = split(self.container)
        canonical = json.dumps(header, sort_keys=True, separators=(",", ":")).encode()
        cases = {
            "vacío": (b"", "truncated"),
            "magia": (b"NOTCERB" + self.container[7:], "bad_magic"),
            "versión": (rebuild(header, ciphertext, version=2), "unknown_version"),
            "truncado": (self.container[:-5], "truncated"),
            "sobrante": (self.container + b"x", "size_mismatch"),
            "no canónica": (rebuild(header, ciphertext, raw=canonical.replace(b",", b", ")), "bad_header"),
            "campo extra": (rebuild({**header, "name": "x"}, ciphertext), "bad_header"),
            "nonce corto": (rebuild({**header, "nonce": "AAAA"}, ciphertext), "bad_header"),
            "longitud": (rebuild({**header, "len": header["len"] + 1}, ciphertext), "truncated"),
            "longitud enorme": (rebuild({**header, "len": MAX + 1}, ciphertext), "bad_header"),
            "id inválido": (rebuild({**header, "doc": "../../etc/passwd"}, ciphertext), "bad_header"),
            "algoritmo": (rebuild({**header, "alg": "AES-128-CBC"}, ciphertext), "bad_header"),
            "cabecera enorme": (crypto.PREFIX.pack(crypto.MAGIC, 1, 10_000) + b"{}", "bad_header"),
        }
        for label, (data, code) in cases.items():
            with self.subTest(label):
                with self.assertRaises(crypto.ContainerError) as caught:
                    crypto.parse_container(data, MAX)
                self.assertEqual(caught.exception.code, code)

    def test_wrapped_key_is_bound_to_its_document(self):
        master = os.urandom(32)
        nonce, wrapped = crypto.wrap_key(master, self.doc_id, self.key)
        self.assertEqual(crypto.unwrap_key(master, self.doc_id, nonce, wrapped), self.key)
        with self.assertRaises(crypto.ContainerError):
            crypto.unwrap_key(master, crypto.new_doc_id(), nonce, wrapped)
        with self.assertRaises(crypto.ContainerError):
            crypto.unwrap_key(os.urandom(32), self.doc_id, nonce, wrapped)


class MasterKey(support.ServiceCase):
    def test_genkey_never_overwrites(self):
        before = self.env.cfg.master_key_file.read_bytes()
        with self.assertRaises(crypto.MasterKeyError):
            crypto.generate_master_key_file(self.env.cfg.master_key_file)
        self.assertEqual(self.env.cfg.master_key_file.read_bytes(), before)

    def _db_snapshot(self) -> bytes:
        return self.env.cfg.db_path.read_bytes()

    def test_missing_key_fails_explicitly_without_creating_one_or_losing_data(self):
        doc, container = self.export()
        self.grant(doc["id"])
        key_file = self.env.cfg.master_key_file
        saved = key_file.read_bytes()
        key_file.unlink()
        db = self._db_snapshot()
        with self.assertRaises(crypto.MasterKeyError) as caught:
            self.env.restart()
        self.assertIn("No se genera una nueva", str(caught.exception))
        self.assertFalse(key_file.exists(), "no debe crearse una clave nueva en silencio")
        self.assertEqual(self._db_snapshot(), db)
        key_file.write_bytes(saved)
        restored = self.env.restart()
        reader = restored.client("lector")
        response = reader.post("/api/open", content=container)
        self.assertEqual(base64.b64decode(response.json()["content_b64"]), support.TEXT)

    def test_wrong_key_fails_explicitly_and_grants_nothing(self):
        doc, container = self.export()
        self.grant(doc["id"])
        key_file = self.env.cfg.master_key_file
        saved = key_file.read_bytes()
        key_file.unlink()
        crypto.generate_master_key_file(key_file)
        db = self._db_snapshot()
        with self.assertRaises(crypto.MasterKeyError) as caught:
            self.env.restart()
        self.assertIn("no coincide", str(caught.exception))
        self.assertEqual(self._db_snapshot(), db)
        key_file.write_bytes(saved)
        self.assertEqual(self.env.restart().client("lector").post("/api/open", content=container).status_code, 200)

    def test_corrupted_key_file_is_rejected(self):
        self.env.cfg.master_key_file.write_text("cerbero-pf-master-v1:no-es-base64!!\n", encoding="ascii")
        with self.assertRaises(crypto.MasterKeyError):
            self.env.restart()

    def test_key_cannot_live_in_data_or_public_directory(self):
        from cerbero_pf.config import STATIC_DIR, ConfigError

        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        for key in (root / "data" / "master.key", STATIC_DIR / "master.key"):
            with self.subTest(key=key), self.assertRaises(ConfigError):
                Config(data_dir=root / "data", master_key_file=key).validate()


if __name__ == "__main__":
    unittest.main()
