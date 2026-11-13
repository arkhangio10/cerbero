"""Contenedor `.cerbero` versión 1 y envoltura de claves con AES-256-GCM (AEAD de `cryptography`).

Formato (todos los enteros en big-endian):

    magic        7 bytes   b"CERBERO"
    version      1 byte    1
    header_len   4 bytes   longitud de la cabecera (1..1024)
    header       JSON canónico UTF-8: {"alg","created","doc","len","nonce","v"}
    ciphertext   len + 16 bytes (texto cifrado y etiqueta GCM)

Los datos adicionales autenticados (AAD) son todos los bytes anteriores al texto cifrado,
de modo que cambiar la versión, el identificador, el nonce o la longitud invalida la etiqueta.
La clave del documento no viaja en el contenedor: se guarda envuelta con la clave maestra en el servidor.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import re
import secrets
import struct
from dataclasses import dataclass
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"CERBERO"
FORMAT_VERSION = 1
ALG = "AES-256-GCM"
PREFIX = struct.Struct(">7sBI")
MAX_HEADER_BYTES = 1024
NONCE_BYTES = 12
TAG_BYTES = 16
KEY_BYTES = 32
DOC_ID_RE = re.compile(r"^pf_[A-Za-z0-9_-]{24}$")
CREATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
HEADER_KEYS = {"alg", "created", "doc", "len", "nonce", "v"}

KEYFILE_PREFIX = "cerbero-pf-master-v1:"
WRAP_AAD = b"cerbero-pf/wrap/v1|"
CHECK_AAD = b"cerbero-pf/key-check/v1"
CHECK_PLAINTEXT = b"cerbero-pf master key check"


class ContainerError(ValueError):
    """El contenedor no cumple el formato o no supera la autenticación."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class MasterKeyError(RuntimeError):
    """Falta la clave maestra, es inválida o no coincide con la base de datos."""


@dataclass(frozen=True)
class ParsedContainer:
    doc_id: str
    nonce: bytes
    length: int
    created: str
    aad: bytes
    ciphertext: bytes


def new_doc_id() -> str:
    return "pf_" + secrets.token_urlsafe(18)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    if not isinstance(text, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", text):
        raise ValueError("base64url inválido")
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def encrypt_container(plaintext: bytes, doc_id: str, created: str, max_plaintext: int) -> tuple[bytes, bytes]:
    """Cifra con una clave aleatoria nueva y devuelve (contenedor, clave_del_documento)."""
    if not DOC_ID_RE.fullmatch(doc_id) or not CREATED_RE.fullmatch(created):
        raise ValueError("identificador o fecha inválidos")
    if len(plaintext) > max_plaintext:
        raise ContainerError("too_large", "el archivo supera el límite de exportación")
    key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(NONCE_BYTES)
    header = _canonical({"alg": ALG, "created": created, "doc": doc_id, "len": len(plaintext),
                         "nonce": _b64(nonce), "v": FORMAT_VERSION})
    prefix = PREFIX.pack(MAGIC, FORMAT_VERSION, len(header)) + header
    return prefix + AESGCM(key).encrypt(nonce, plaintext, prefix), key


def parse_container(data: bytes, max_plaintext: int) -> ParsedContainer:
    """Valida el formato de forma estricta, sin descifrar."""
    if len(data) < PREFIX.size:
        raise ContainerError("truncated", "archivo truncado o vacío")
    magic, version, header_len = PREFIX.unpack_from(data)
    if magic != MAGIC:
        raise ContainerError("bad_magic", "no es un contenedor .cerbero")
    if version != FORMAT_VERSION:
        raise ContainerError("unknown_version", f"versión de contenedor desconocida: {version}")
    if not 0 < header_len <= MAX_HEADER_BYTES:
        raise ContainerError("bad_header", "longitud de cabecera fuera de rango")
    end = PREFIX.size + header_len
    if len(data) < end:
        raise ContainerError("truncated", "cabecera truncada")
    raw = data[PREFIX.size:end]
    try:
        header = json.loads(raw.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ContainerError("bad_header", "cabecera ilegible") from None
    if not isinstance(header, dict) or set(header) != HEADER_KEYS or _canonical(header) != raw:
        raise ContainerError("bad_header", "cabecera no canónica o con campos inesperados")
    if header["v"] != FORMAT_VERSION or header["alg"] != ALG:
        raise ContainerError("bad_header", "algoritmo o versión de cabecera no admitidos")
    doc_id, length, created = header["doc"], header["len"], header["created"]
    if not isinstance(doc_id, str) or not DOC_ID_RE.fullmatch(doc_id):
        raise ContainerError("bad_header", "identificador de documento inválido")
    if not isinstance(created, str) or not CREATED_RE.fullmatch(created):
        raise ContainerError("bad_header", "fecha de cabecera inválida")
    if type(length) is not int or not 0 <= length <= max_plaintext:
        raise ContainerError("bad_header", "longitud declarada fuera de rango")
    try:
        nonce = _unb64(header["nonce"])
    except (ValueError, binascii.Error):
        raise ContainerError("bad_header", "nonce inválido") from None
    if len(nonce) != NONCE_BYTES:
        raise ContainerError("bad_header", "nonce de longitud incorrecta")
    ciphertext = data[end:]
    if len(ciphertext) < length + TAG_BYTES:
        raise ContainerError("truncated", "contenido cifrado truncado")
    if len(ciphertext) > length + TAG_BYTES:
        raise ContainerError("size_mismatch", "datos sobrantes tras el contenido cifrado")
    return ParsedContainer(doc_id, nonce, length, created, data[:end], ciphertext)


def decrypt_container(parsed: ParsedContainer, key: bytes) -> bytes:
    try:
        plaintext = AESGCM(key).decrypt(parsed.nonce, parsed.ciphertext, parsed.aad)
    except InvalidTag:
        raise ContainerError("auth_failed", "la comprobación de autenticación del contenedor falló") from None
    if len(plaintext) != parsed.length:
        raise ContainerError("size_mismatch", "longitud descifrada distinta de la declarada")
    return plaintext


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# Clave maestra ---------------------------------------------------------------

def generate_master_key_file(path: Path) -> str:
    """Crea un archivo de clave nuevo. Nunca sobrescribe uno existente."""
    path.parent.mkdir(parents=True, exist_ok=True)
    key = AESGCM.generate_key(bit_length=256)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
    except FileExistsError:
        raise MasterKeyError(f"ya existe una clave maestra en {path}; no se sobrescribe") from None
    with os.fdopen(fd, "w", encoding="ascii", newline="\n") as handle:
        handle.write(KEYFILE_PREFIX + base64.b64encode(key).decode("ascii") + "\n")
    return key_id(key)


def load_master_key(path: Path) -> bytes:
    if not path.is_file():
        raise MasterKeyError(
            f"no se encontró la clave maestra en {path}. No se genera una nueva automáticamente: "
            "restaura la clave original o, sólo para una instalación nueva, ejecuta `genkey`.")
    text = path.read_text(encoding="ascii", errors="strict").strip()
    if not text.startswith(KEYFILE_PREFIX):
        raise MasterKeyError(f"el archivo {path} no tiene el formato de clave maestra esperado")
    try:
        key = base64.b64decode(text[len(KEYFILE_PREFIX):], validate=True)
    except binascii.Error:
        raise MasterKeyError(f"la clave maestra de {path} no es base64 válido") from None
    if len(key) != KEY_BYTES:
        raise MasterKeyError(f"la clave maestra de {path} no tiene 32 bytes")
    return key


def key_id(key: bytes) -> str:
    return hashlib.sha256(b"cerbero-pf/key-id/v1|" + key).hexdigest()[:16]


def make_key_check(key: bytes) -> bytes:
    nonce = os.urandom(NONCE_BYTES)
    return nonce + AESGCM(key).encrypt(nonce, CHECK_PLAINTEXT, CHECK_AAD)


def key_check_matches(key: bytes, blob: bytes) -> bool:
    try:
        return AESGCM(key).decrypt(blob[:NONCE_BYTES], blob[NONCE_BYTES:], CHECK_AAD) == CHECK_PLAINTEXT
    except InvalidTag:
        return False


def wrap_key(master: bytes, doc_id: str, doc_key: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(NONCE_BYTES)
    return nonce, AESGCM(master).encrypt(nonce, doc_key, WRAP_AAD + doc_id.encode("ascii"))


def unwrap_key(master: bytes, doc_id: str, nonce: bytes, wrapped: bytes) -> bytes:
    try:
        return AESGCM(master).decrypt(nonce, wrapped, WRAP_AAD + doc_id.encode("ascii"))
    except InvalidTag:
        raise ContainerError("key_unwrap_failed", "no se pudo desenvolver la clave del documento") from None
