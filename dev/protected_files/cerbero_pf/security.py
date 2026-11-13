"""Contraseñas, saneamiento de nombres y texto, y clasificación de formatos."""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import unicodedata

USERNAME_RE = re.compile(r"^[a-z0-9_.-]{3,32}$")
_SCRYPT = {"n": 2 ** 14, "r": 8, "p": 1, "dklen": 32}
_WINDOWS_RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
_FORBIDDEN_IN_NAMES = set('<>:"|?*')

TEXT_MEDIA = "text/plain; charset=utf-8"
ACTIVE_MEDIA = "application/x-cerbero-active"
OTHER_MEDIA = "application/octet-stream"
VIEWABLE_MEDIA = {TEXT_MEDIA, "image/png", "image/jpeg", "image/gif", "image/webp"}
_TEXT_EXT = {"", ".txt", ".md", ".csv", ".log", ".json"}
_ACTIVE_EXT = {
    ".htm", ".html", ".xhtml", ".shtml", ".svg", ".svgz", ".xml", ".xsl", ".js", ".mjs", ".hta", ".php",
    ".exe", ".dll", ".msi", ".scr", ".bat", ".cmd", ".com", ".ps1", ".psm1", ".vbs", ".vbe", ".wsf", ".jar",
    ".lnk", ".sh", ".py", ".docm", ".dotm", ".xlsm", ".xltm", ".xlam", ".pptm", ".potm", ".ppam", ".swf",
}
_ACTIVE_PREFIXES = (b"<svg", b"<?xml", b"<!doctype html", b"<html", b"<script", b"<head", b"<body", b"<iframe")


def hash_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    salt = salt or os.urandom(16)
    return salt, hashlib.scrypt(password.encode("utf-8"), salt=salt, **_SCRYPT)


def verify_password(password: str, salt: bytes, expected: bytes) -> bool:
    return hmac.compare_digest(hash_password(password, salt)[1], expected)


def clean_text(value: str | None, limit: int) -> str:
    """Quita caracteres de control y de formato (incluidos los de dirección bidi) y recorta."""
    if not value:
        return ""
    value = unicodedata.normalize("NFC", str(value))
    kept = "".join(" " if ch in "\t\r\n" else ch for ch in value
                   if ch in "\t\r\n" or unicodedata.category(ch) not in ("Cc", "Cf", "Cs", "Co", "Cn"))
    return " ".join(kept.split())[:limit]


def display_name(raw: str | None) -> str:
    """Nombre visible a partir del nombre de archivo enviado: sin rutas, controles ni nombres reservados."""
    base = clean_text((raw or "").replace("\\", "/").split("/")[-1], 120)
    base = "".join("_" if ch in _FORBIDDEN_IN_NAMES else ch for ch in base).strip(" .")
    if not base:
        return "documento"
    stem = base.split(".")[0].lower()
    return "_" + base if stem in _WINDOWS_RESERVED else base


def container_name(name: str) -> str:
    stem = name.rsplit(".", 1)[0] if "." in name.strip(".") else name
    return (stem.strip(" .") or "documento") + ".cerbero"


def classify_media(name: str, data: bytes) -> str:
    """Tipo según el contenido y la extensión, nunca según lo que declare el cliente."""
    ext = ("." + name.rsplit(".", 1)[1].lower()) if "." in name else ""
    head = data[:1024].lstrip(b"\xef\xbb\xbf \t\r\n").lower()
    if ext in _ACTIVE_EXT or head.startswith(_ACTIVE_PREFIXES):
        return ACTIVE_MEDIA
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if ext in _TEXT_EXT and b"\x00" not in data:
        try:
            data.decode("utf-8", errors="strict")
            return TEXT_MEDIA
        except UnicodeDecodeError:
            pass
    return OTHER_MEDIA
