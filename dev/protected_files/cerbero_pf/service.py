"""Lógica del servicio: cuentas, exportación, permisos, apertura, revocación, auditoría y avisos.

Toda decisión de acceso se toma dentro de una transacción `BEGIN IMMEDIATE` que también escribe el evento
de auditoría. El contenido sólo se devuelve después de confirmar esa transacción; si la auditoría no se
puede persistir, no se entrega nada.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from . import crypto, geo, store
from .config import Config
from .mail import SmtpSender
from .security import (USERNAME_RE, VIEWABLE_MEDIA, classify_media, clean_text, container_name, display_name,
                       hash_password, verify_password)

STATE_TEXT = {"lost": "marcado como extraviado", "revoked": "revocado"}
DENIAL_TEXT = {
    "document_lost": "marcado como extraviado",
    "document_revoked": "revocado por su propietario",
    "no_permission": "con una cuenta sin permiso de lectura",
    "grant_revoked": "con una cuenta cuyo permiso fue revocado",
    "integrity_failure": "y falló la comprobación de integridad en el servidor",
}
NOTICE = ("Este aviso no prueba que alguien haya leído el contenido ni identifica a una persona. "
          "No se adjunta contenido, claves ni coordenadas.")


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


class AuditUnavailable(ServiceError):
    def __init__(self):
        super().__init__(503, "audit_unavailable",
                         "Servicio no disponible: no se pudo registrar la solicitud, así que no se concede acceso.")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stamp(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class Session:
    user_id: int
    username: str
    display_name: str
    csrf_token: str
    token_hash: str


@dataclass(frozen=True)
class RequestContext:
    ip: str = "desconocida"
    ip_source: str = "conexión"
    forwarded_header: str = ""
    user_agent: str = ""
    client_location_raw: str | None = None


@dataclass
class OpenResult:
    result: str
    reason: str
    message: str
    event_id: int | None = None
    document: dict | None = None
    content: bytes | None = field(default=None, repr=False)


class Service:
    def __init__(self, cfg: Config, now: Callable[[], datetime] = utc_now, sender=None):
        self.cfg = cfg
        self.now = now
        self.sender = sender if sender is not None else SmtpSender(cfg.smtp)
        self.master_key = crypto.load_master_key(cfg.master_key_file)
        self.geo = geo.build_provider(cfg.geo_provider, cfg.geo_csv_path)
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        cfg.containers_dir.mkdir(exist_ok=True)
        store.initialize(cfg.db_path)
        self._check_master_key()

    # Infraestructura -------------------------------------------------------

    def connect(self) -> sqlite3.Connection:
        return store.connect(self.cfg.db_path)

    def _check_master_key(self) -> None:
        conn = self.connect()
        try:
            with store.write_tx(conn):
                row = conn.execute("SELECT value FROM meta WHERE key = 'key_check'").fetchone()
                if row is None:
                    if conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]:
                        raise crypto.MasterKeyError("la base tiene documentos pero no la comprobación de clave; "
                                                    "no se continúa")
                    conn.execute("INSERT INTO meta VALUES ('key_check', ?)", (crypto.make_key_check(self.master_key),))
                    conn.execute("INSERT INTO meta VALUES ('key_id', ?)", (crypto.key_id(self.master_key),))
                elif not crypto.key_check_matches(self.master_key, row["value"]):
                    stored = conn.execute("SELECT value FROM meta WHERE key = 'key_id'").fetchone()
                    raise crypto.MasterKeyError(
                        f"la clave maestra de {self.cfg.master_key_file} (id {crypto.key_id(self.master_key)}) no "
                        f"coincide con la usada por esta base (id {stored['value'] if stored else '?'}). "
                        "No se genera otra: restaura la clave correcta.")
        finally:
            conn.close()

    def _ts(self) -> str:
        return stamp(self.now())

    # Cuentas y sesiones ------------------------------------------------------

    def create_user(self, username: str, password: str, display: str = "", notify_email: str = "") -> int:
        if not USERNAME_RE.fullmatch(username):
            raise ServiceError(400, "bad_username", "usuario: 3-32 caracteres a-z, 0-9, punto, guion o guion bajo")
        if len(password) < 12:
            raise ServiceError(400, "weak_password", "la contraseña debe tener al menos 12 caracteres")
        email = clean_text(notify_email, 200)
        if email and ("@" not in email or " " in email):
            raise ServiceError(400, "bad_email", "correo de aviso inválido")
        salt, digest = hash_password(password)
        conn = self.connect()
        try:
            with store.write_tx(conn):
                cur = conn.execute(
                    "INSERT INTO users (username, display_name, notify_email, pw_salt, pw_hash, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (username, clean_text(display, 60) or username, email or None, salt, digest, self._ts()))
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise ServiceError(409, "user_exists", "ya existe esa cuenta") from None
        finally:
            conn.close()

    def login(self, username: str, password: str, ip: str) -> tuple[str, Session]:
        username = clean_text(username, 64).lower()
        now = self.now()
        since = stamp(now - timedelta(minutes=self.cfg.login_window_minutes))
        conn = self.connect()
        try:
            with store.write_tx(conn):  # cada intento reserva su fallo antes de comprobar: sin carreras
                failures = conn.execute(
                    "SELECT (SELECT COUNT(*) FROM login_failures WHERE username = ? AND at_utc >= ?), "
                    "(SELECT COUNT(*) FROM login_failures WHERE ip = ? AND at_utc >= ?)",
                    (username, since, ip, since)).fetchone()
                if max(failures) >= self.cfg.login_max_failures:
                    raise ServiceError(429, "login_locked", "Demasiados intentos fallidos. Espera antes de reintentar.")
                conn.execute("INSERT INTO login_failures (username, ip, at_utc) VALUES (?, ?, ?)",
                             (username, ip, stamp(now)))
                user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            ok = verify_password(password, user["pw_salt"], user["pw_hash"]) if user else \
                verify_password(password, b"\0" * 16, b"\0" * 32)
            if not (user and ok):
                raise ServiceError(401, "bad_credentials", "Usuario o contraseña incorrectos.")
            token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            with store.write_tx(conn):
                conn.execute("DELETE FROM login_failures WHERE username = ?", (username,))
                conn.execute("INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
                             (token_hash, user["id"], csrf, stamp(now),
                              stamp(now + timedelta(hours=self.cfg.session_hours))))
            return token, Session(user["id"], user["username"], user["display_name"], csrf, token_hash)
        finally:
            conn.close()

    def session(self, token: str | None) -> Session | None:
        if not token or len(token) > 128:
            return None
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        conn = self.connect()
        try:
            row = conn.execute(
                "SELECT s.token_hash, s.csrf_token, s.expires_at, u.id, u.username, u.display_name "
                "FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ?", (token_hash,)).fetchone()
        finally:
            conn.close()
        if row is None or row["expires_at"] <= self._ts():
            return None
        return Session(row["id"], row["username"], row["display_name"], row["csrf_token"], row["token_hash"])

    def logout(self, session: Session) -> None:
        conn = self.connect()
        try:
            with store.write_tx(conn):
                conn.execute("DELETE FROM sessions WHERE token_hash = ?", (session.token_hash,))
        finally:
            conn.close()

    @staticmethod
    def csrf_ok(session: Session, presented: str | None) -> bool:
        return bool(presented) and hmac.compare_digest(session.csrf_token.encode(), presented.encode())

    # Eventos y avisos -------------------------------------------------------------

    def _event(self, conn, ctx: RequestContext, *, kind: str, result: str, reason: str, verified: bool,
               doc: sqlite3.Row | None = None, claimed: str | None = None, actor: Session | None = None,
               geo_info: dict | None = None, client_loc: dict | None = None, detail: str = "") -> int:
        cur = conn.execute(
            "INSERT INTO events (at_utc, kind, result, reason, verified, doc_id, claimed_doc_id, owner_id, "
            "actor_user_id, actor_label, ip, ip_source, forwarded_header, geo, client_location, user_agent, detail) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self._ts(), kind, result, reason, int(verified), doc["id"] if doc else None, claimed,
             doc["owner_id"] if doc else None, actor.user_id if actor else None,
             actor.username if actor else "sin sesión", ctx.ip, ctx.ip_source, ctx.forwarded_header,
             json.dumps(geo_info or {}, ensure_ascii=False), json.dumps(client_loc or {"status": "not_requested"}),
             clean_text(ctx.user_agent, 200), clean_text(detail, 300)))
        return cur.lastrowid

    def _notify(self, conn, doc: sqlite3.Row, event_id: int, reason: str, actor: Session | None,
                geo_info: dict, client_loc: dict) -> None:
        now = self.now()
        actor_text = f"la cuenta «{actor.username}»" if actor else "una sesión sin autenticar"
        dedup_key = f"{doc['id']}|{reason}|{actor.username if actor else '-'}"
        window = stamp(now - timedelta(minutes=self.cfg.dedup_window_minutes))
        existing = conn.execute(
            "SELECT id FROM notifications WHERE owner_id = ? AND dedup_key = ? AND last_at >= ? "
            "ORDER BY id DESC LIMIT 1", (doc["owner_id"], dedup_key, window)).fetchone()
        if existing:
            conn.execute("UPDATE notifications SET count = count + 1, last_at = ?, last_event_id = ?, read_at = NULL "
                         "WHERE id = ?", (stamp(now), event_id, existing["id"]))
            return
        title = f"Acceso denegado: {doc['container_name']}"
        declared = "sí (detalle sólo en el panel)" if client_loc.get("status") == "declared" else "no"
        body = (f"Se intentó acceder a {doc['container_name']}, {DENIAL_TEXT[reason]}. Acceso denegado. "
                f"Origen: {actor_text}. Ubicación aproximada por IP: {geo.describe_location(geo_info)}. "
                f"Ubicación declarada por el navegador: {declared}.")
        owner = conn.execute("SELECT notify_email FROM users WHERE id = ?", (doc["owner_id"],)).fetchone()
        smtp = self.cfg.smtp
        if not smtp.enabled:
            email_state = "disabled"
        elif not owner["notify_email"]:
            email_state = "no_recipient"
        elif conn.execute("SELECT COUNT(*) FROM email_outbox WHERE owner_id = ? AND created_at >= ?",
                          (doc["owner_id"], stamp(now - timedelta(hours=1)))).fetchone()[0] >= smtp.hourly_cap_per_owner:
            email_state = "burst_skipped"
        else:
            email_state = "queued"
        cur = conn.execute(
            "INSERT INTO notifications (owner_id, doc_id, first_event_id, last_event_id, dedup_key, title, body, "
            "first_at, last_at, count, email_state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)",
            (doc["owner_id"], doc["id"], event_id, event_id, dedup_key, title, body, stamp(now), stamp(now), email_state))
        if email_state == "queued":
            email_body = (f"{body}\n\n{NOTICE}\nRevisa el detalle en el panel autenticado: {self.cfg.base_url}/panel\n")
            conn.execute(
                "INSERT INTO email_outbox (notification_id, owner_id, recipient, subject, body, status, max_attempts, "
                "next_attempt_at, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?)",
                (cur.lastrowid, doc["owner_id"], owner["notify_email"], f"Cerbero: {title}", email_body,
                 smtp.max_attempts, stamp(now), stamp(now)))

    # Documentos ---------------------------------------------------------------

    def export_document(self, owner: Session, raw_name: str, data: bytes, ctx: RequestContext,
                        source: str = "web") -> tuple[dict, bytes]:
        if not data:
            raise ServiceError(400, "empty_file", "El archivo está vacío.")
        if len(data) > self.cfg.max_plaintext_bytes:
            raise ServiceError(413, "too_large",
                               f"El archivo supera el límite de exportación ({self.cfg.max_plaintext_bytes} bytes).")
        name = display_name(raw_name)
        doc_id, created = crypto.new_doc_id(), self.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        container, doc_key = crypto.encrypt_container(data, doc_id, created, self.cfg.max_plaintext_bytes)
        wrap_nonce, wrapped = crypto.wrap_key(self.master_key, doc_id, doc_key)
        path = self.cfg.containers_dir / f"{doc_id}.cerbero"
        with open(path, "xb") as handle:
            handle.write(container)
        conn = self.connect()
        try:
            with store.write_tx(conn):
                conn.execute(
                    "INSERT INTO documents (id, owner_id, display_name, container_name, media_type, size, "
                    "container_sha256, wrap_nonce, wrapped_key, master_key_id, state, source, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)",
                    (doc_id, owner.user_id, name, container_name(name), classify_media(name, data), len(data),
                     crypto.sha256_hex(container), wrap_nonce, wrapped, crypto.key_id(self.master_key), source,
                     self._ts()))
                doc = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
                self._event(conn, ctx, kind="export", result="ok", reason="exported", verified=True, doc=doc,
                            actor=owner, geo_info={})
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        finally:
            conn.close()
        return self._doc_dict(doc), container

    def local_session(self, username: str) -> Session:
        """Identidad para órdenes locales: quien las ejecuta ya controla la configuración y la clave maestra."""
        conn = self.connect()
        try:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        finally:
            conn.close()
        if user is None:
            raise ServiceError(404, "no_user", "No existe esa cuenta.")
        return Session(user["id"], user["username"], user["display_name"], "", "")

    def export_path(self, owner_username: str, source: Path) -> tuple[dict, Path]:
        """Exportación desde una ruta del área autorizada (equivalente local a elegir un archivo del NAS)."""
        roots = [r.resolve(strict=True) for r in self.cfg.export_roots if r.is_dir()]
        if not roots or self.cfg.export_output_dir is None:
            raise ServiceError(400, "no_export_roots", "No hay raíces de exportación ni carpeta de salida configuradas.")
        source = Path(source)
        try:
            real = source.resolve(strict=True)
        except (FileNotFoundError, OSError):
            raise ServiceError(404, "not_found", "No existe el archivo indicado.") from None
        if not any(real.is_relative_to(root) for root in roots):
            raise ServiceError(403, "outside_roots", "La ruta está fuera del área autorizada para exportar.")
        if source.is_symlink() or not real.is_file():
            raise ServiceError(400, "not_regular", "Sólo se exportan archivos normales, no enlaces ni carpetas.")
        if real.stat().st_size > self.cfg.max_plaintext_bytes:
            raise ServiceError(413, "too_large", "El archivo supera el límite de exportación.")
        owner = self.local_session(owner_username)
        with open(real, "rb") as handle:
            opened, now = os.fstat(handle.fileno()), real.stat()
            if (opened.st_dev, opened.st_ino) != (now.st_dev, now.st_ino) or source.resolve(strict=True) != real:
                raise ServiceError(409, "path_changed", "La ruta cambió mientras se abría; no se exporta.")
            data = handle.read(self.cfg.max_plaintext_bytes + 1)
        doc, container = self.export_document(owner, real.name, data, RequestContext(ip="local", ip_source="CLI"),
                                              source="cli")
        out_dir = self.cfg.export_output_dir.resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / doc["container_name"]
        if out.exists():
            out = out_dir / f"{out.stem}-{doc['id'][3:11]}.cerbero"
        with open(out, "xb") as handle:
            handle.write(container)
        return doc, out

    @staticmethod
    def _doc_dict(row: sqlite3.Row) -> dict:
        return {key: row[key] for key in ("id", "display_name", "container_name", "media_type", "size", "state",
                                          "source", "created_at", "state_changed_at", "container_sha256")}

    def _owned(self, conn, owner: Session, doc_id: str) -> sqlite3.Row:
        row = None
        if crypto.DOC_ID_RE.fullmatch(doc_id or ""):
            row = conn.execute("SELECT * FROM documents WHERE id = ? AND owner_id = ?",
                               (doc_id, owner.user_id)).fetchone()
        if row is None:
            raise ServiceError(404, "not_found", "Documento no encontrado.")
        return row

    def list_documents(self, owner: Session) -> list[dict]:
        conn = self.connect()
        try:
            docs = []
            for row in conn.execute("SELECT * FROM documents WHERE owner_id = ? ORDER BY created_at DESC",
                                    (owner.user_id,)).fetchall():
                item = self._doc_dict(row)
                item["grants"] = self._grants(conn, row["id"])
                docs.append(item)
            return docs
        finally:
            conn.close()

    @staticmethod
    def _grants(conn, doc_id: str) -> list[dict]:
        return [dict(r) for r in conn.execute(
            "SELECT u.username, g.granted_at, g.revoked_at FROM grants g JOIN users u ON u.id = g.user_id "
            "WHERE g.doc_id = ? ORDER BY g.id", (doc_id,)).fetchall()]

    def get_document(self, owner: Session, doc_id: str) -> dict:
        conn = self.connect()
        try:
            row = self._owned(conn, owner, doc_id)
            return {**self._doc_dict(row), "grants": self._grants(conn, row["id"])}
        finally:
            conn.close()

    def container_bytes(self, owner: Session, doc_id: str) -> tuple[str, bytes]:
        conn = self.connect()
        try:
            row = self._owned(conn, owner, doc_id)
        finally:
            conn.close()
        data = (self.cfg.containers_dir / f"{row['id']}.cerbero").read_bytes()
        if crypto.sha256_hex(data) != row["container_sha256"]:
            raise ServiceError(500, "container_mismatch", "La copia guardada del contenedor no coincide con su registro.")
        return row["container_name"], data

    def set_grant(self, owner: Session, doc_id: str, username: str, allow: bool, ctx: RequestContext) -> dict:
        conn = self.connect()
        try:
            with store.write_tx(conn):
                doc = self._owned(conn, owner, doc_id)
                if doc["state"] != "active":
                    raise ServiceError(409, "not_active", "El documento ya no está activo.")
                user = conn.execute("SELECT id, username FROM users WHERE username = ?",
                                    (clean_text(username, 64).lower(),)).fetchone()
                if user is None:
                    raise ServiceError(404, "no_user", "No existe esa cuenta.")
                if user["id"] == owner.user_id:
                    raise ServiceError(400, "self_grant", "El propietario ya tiene acceso.")
                active = conn.execute("SELECT id FROM grants WHERE doc_id = ? AND user_id = ? AND revoked_at IS NULL",
                                      (doc_id, user["id"])).fetchone()
                if allow and not active:
                    conn.execute("INSERT INTO grants (doc_id, user_id, granted_at) VALUES (?, ?, ?)",
                                 (doc_id, user["id"], self._ts()))
                elif not allow and active:
                    conn.execute("UPDATE grants SET revoked_at = ? WHERE id = ?", (self._ts(), active["id"]))
                else:
                    raise ServiceError(409, "no_change", "El permiso ya estaba en ese estado.")
                self._event(conn, ctx, kind="permission_change", result="ok", verified=True, doc=doc, actor=owner,
                            reason="grant_added" if allow else "grant_revoked", detail=f"cuenta {user['username']}",
                            geo_info={})
            return self.get_document(owner, doc_id)
        finally:
            conn.close()

    def set_state(self, owner: Session, doc_id: str, state: str, confirm_doc_id: str, ctx: RequestContext) -> dict:
        """Marca extraviado o revoca. La operación es efectiva en el COMMIT; se devuelve ese momento."""
        if state not in STATE_TEXT:
            raise ServiceError(400, "bad_state", "Estado no admitido.")
        if confirm_doc_id != doc_id:
            raise ServiceError(400, "not_confirmed", "Confirma la operación con el identificador del documento.")
        conn = self.connect()
        try:
            with store.write_tx(conn):
                doc = self._owned(conn, owner, doc_id)
                if doc["state"] == "revoked" or doc["state"] == state:
                    raise ServiceError(409, "no_change", f"El documento ya está {STATE_TEXT[doc['state']]}.")
                effective = self._ts()
                conn.execute("UPDATE documents SET state = ?, state_changed_at = ? WHERE id = ?",
                             (state, effective, doc_id))
                event_id = self._event(conn, ctx, kind="revocation", result="applied", verified=True, doc=doc,
                                       actor=owner, reason="marked_lost" if state == "lost" else "revoked",
                                       geo_info={})
            return {**self.get_document(owner, doc_id), "effective_at": effective, "event_id": event_id}
        finally:
            conn.close()

    # Apertura ---------------------------------------------------------------------

    def open_container(self, data: bytes, actor: Session | None, ctx: RequestContext) -> OpenResult:
        received = self._ts()
        client_loc = geo.client_location(ctx.client_location_raw, received)
        geo_info = geo.locate(ctx.ip, self.geo)
        common = {"actor": actor, "geo_info": geo_info, "client_loc": client_loc}
        digest = crypto.sha256_hex(data)
        conn = self.connect()
        try:
            with store.write_tx(conn):  # límite, validación, decisión y evento: una sola escritura serializada
                recent = conn.execute(
                    "SELECT COUNT(*) FROM events WHERE ip = ? AND at_utc >= ? AND kind IN "
                    "('access_request','access_denied','content_served','container_invalid','integrity_failure')",
                    (ctx.ip, stamp(self.now() - timedelta(minutes=1)))).fetchone()[0]
                if recent >= self.cfg.open_attempts_per_minute:
                    return OpenResult("rate_limited", "too_many_attempts",
                                      "Demasiados intentos desde esta conexión. Espera un minuto.")
                try:
                    parsed = crypto.parse_container(data, self.cfg.max_plaintext_bytes)
                except crypto.ContainerError as exc:
                    event_id = self._event(conn, ctx, kind="container_invalid", result="rejected", reason=exc.code,
                                           verified=False, **common)
                    return OpenResult("invalid", exc.code, "Archivo inválido: el contenedor está dañado, truncado o "
                                      "tiene un formato desconocido. No se entrega contenido.", event_id)
                doc = conn.execute("SELECT * FROM documents WHERE id = ?", (parsed.doc_id,)).fetchone()
                if doc is None or not hmac.compare_digest(doc["container_sha256"], digest):
                    reason = "unknown_document" if doc is None else "does_not_match_registered_export"
                    event_id = self._event(conn, ctx, kind="container_invalid", result="rejected", reason=reason,
                                           verified=False, claimed=parsed.doc_id, **common)
                    return OpenResult("invalid", reason, "Archivo inválido: no coincide con ninguna exportación "
                                      "registrada. No se entrega contenido.", event_id)
                summary = {"name": doc["container_name"], "state": doc["state"]}
                if doc["state"] != "active":
                    reason = "document_lost" if doc["state"] == "lost" else "document_revoked"
                    return self._deny(conn, ctx, doc, reason, common, summary)
                if actor is None:
                    event_id = self._event(conn, ctx, kind="access_request", result="auth_required",
                                           reason="authentication_required", verified=True, doc=doc, **common)
                    return OpenResult("auth_required", "authentication_required",
                                      "Inicia sesión para que el servicio compruebe tu permiso.",
                                      event_id, summary)
                if actor.user_id != doc["owner_id"]:
                    grant = conn.execute(
                        "SELECT revoked_at FROM grants WHERE doc_id = ? AND user_id = ? "
                        "ORDER BY revoked_at IS NULL DESC, id DESC LIMIT 1", (doc["id"], actor.user_id)).fetchone()
                    if grant is None or grant["revoked_at"] is not None:
                        return self._deny(conn, ctx, doc, "no_permission" if grant is None else "grant_revoked",
                                          common, summary)
                if doc["media_type"] not in VIEWABLE_MEDIA:
                    event_id = self._event(conn, ctx, kind="access_denied", result="denied", verified=True, doc=doc,
                                           reason="unsupported_format", detail=doc["media_type"], **common)
                    return OpenResult("unsupported", "unsupported_format",
                                      "Formato no soportado por el visor: el contenido no se entrega ni se ejecuta.",
                                      event_id, summary)
                try:
                    key = crypto.unwrap_key(self.master_key, doc["id"], doc["wrap_nonce"], doc["wrapped_key"])
                    plaintext = crypto.decrypt_container(parsed, key)
                except crypto.ContainerError as exc:
                    return self._deny(conn, ctx, doc, "integrity_failure", common, summary, kind="integrity_failure",
                                      detail=exc.code)
                event_id = self._event(conn, ctx, kind="content_served", result="served", verified=True, doc=doc,
                                       reason="authorized_owner" if actor.user_id == doc["owner_id"] else "authorized_reader",
                                       **common)
            return OpenResult("allowed", "authorized",
                              "El servicio entregó el contenido al visor; esto no prueba que se haya leído.",
                              event_id, {**summary, "media_type": doc["media_type"], "size": doc["size"]}, plaintext)
        except sqlite3.Error:
            raise AuditUnavailable() from None
        finally:
            conn.close()

    def _deny(self, conn, ctx, doc, reason, common, summary, kind="access_denied", detail="") -> OpenResult:
        event_id = self._event(conn, ctx, kind=kind, result="denied", reason=reason, verified=True, doc=doc,
                               detail=detail, **common)
        actor = common["actor"]
        if not (actor and actor.user_id == doc["owner_id"]):
            try:
                conn.execute("SAVEPOINT notify")
                self._notify(conn, doc, event_id, reason, actor, common["geo_info"], common["client_loc"])
                conn.execute("RELEASE notify")
            except sqlite3.Error:
                conn.execute("ROLLBACK TO notify")
        messages = {
            "document_lost": "Acceso denegado: el propietario marcó este documento como extraviado.",
            "document_revoked": "Acceso denegado: el propietario revocó este documento.",
            "no_permission": "Acceso denegado: tu cuenta no tiene permiso para este documento.",
            "grant_revoked": "Acceso denegado: el propietario revocó tu permiso.",
            "integrity_failure": "La comprobación de integridad falló en el servidor; no se entrega contenido. "
                                 "Esto no prueba por sí solo un ataque.",
        }
        return OpenResult("denied", reason, messages[reason], event_id, summary)

    # Consultas del propietario ---------------------------------------------------

    @staticmethod
    def _event_dict(row: sqlite3.Row) -> dict:
        item = dict(row)
        item["geo"] = json.loads(item["geo"])
        item["geo_text"] = geo.describe_location(item["geo"]) if item["geo"] else ""
        item["client_location"] = json.loads(item["client_location"])
        item["verified"] = bool(item["verified"])
        return item

    def events(self, owner: Session, doc_id: str | None = None, limit: int = 200) -> list[dict]:
        conn = self.connect()
        try:
            if doc_id:
                self._owned(conn, owner, doc_id)
            rows = conn.execute(
                "SELECT e.*, d.container_name FROM events e LEFT JOIN documents d ON d.id = e.doc_id "
                "WHERE e.owner_id = ? AND e.verified = 1 AND (? IS NULL OR e.doc_id = ?) ORDER BY e.id DESC LIMIT ?",
                (owner.user_id, doc_id, doc_id, min(limit, 500))).fetchall()
            return [self._event_dict(r) for r in rows]
        finally:
            conn.close()

    def telemetry(self, owner: Session, limit: int = 100) -> list[dict]:
        """Intentos no verificados que mencionan un ID propio: no prueban que se trate de tu documento."""
        conn = self.connect()
        try:
            rows = conn.execute(
                "SELECT e.* FROM events e WHERE e.verified = 0 AND e.claimed_doc_id IN "
                "(SELECT id FROM documents WHERE owner_id = ?) ORDER BY e.id DESC LIMIT ?",
                (owner.user_id, min(limit, 500))).fetchall()
            return [self._event_dict(r) for r in rows]
        finally:
            conn.close()

    def notifications(self, owner: Session) -> list[dict]:
        conn = self.connect()
        try:
            rows = conn.execute(
                "SELECT n.*, o.status AS email_status, o.attempts AS email_attempts, o.max_attempts AS email_max, "
                "o.last_error AS email_error, o.sent_at AS email_sent_at, o.recipient AS email_recipient "
                "FROM notifications n LEFT JOIN email_outbox o ON o.notification_id = n.id "
                "WHERE n.owner_id = ? ORDER BY n.last_at DESC LIMIT 200", (owner.user_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def mark_read(self, owner: Session, notification_id: int) -> None:
        conn = self.connect()
        try:
            with store.write_tx(conn):
                cur = conn.execute("UPDATE notifications SET read_at = ? WHERE id = ? AND owner_id = ?",
                                   (self._ts(), notification_id, owner.user_id))
                if cur.rowcount == 0:
                    raise ServiceError(404, "not_found", "Aviso no encontrado.")
        finally:
            conn.close()

    def audit_export(self, owner: Session, doc_id: str) -> dict:
        """Registro exportable para revisión manual. La Skill no lo consume automáticamente."""
        document = self.get_document(owner, doc_id)
        return {
            "format": "cerbero-pf-audit-1",
            "generated_at": self._ts(),
            "document": document,
            "events": self.events(owner, doc_id, limit=500),
            "notifications": [n for n in self.notifications(owner) if n["doc_id"] == doc_id],
            "limits": [
                "Los eventos registran solicitudes al servicio; no prueban que una persona leyó el contenido.",
                "La ubicación por IP es aproximada y la declarada por el navegador puede manipularse.",
                "No se detecta el descifrado fuera del servicio ni se rastrea el archivo fuera del visor.",
                "Revocar no borra contenido ya entregado.",
            ],
        }

    # Cola de correo ------------------------------------------------------------------

    def process_outbox(self, limit: int = 10) -> dict:
        """Envía los correos pendientes vencidos. Reintentos limitados; `sent` sólo tras aceptación SMTP."""
        counts = {"sent": 0, "retry": 0, "failed": 0}
        if not self.cfg.smtp.enabled:
            return counts
        conn = self.connect()
        try:
            due = conn.execute("SELECT * FROM email_outbox WHERE status = 'pending' AND next_attempt_at <= ? "
                               "ORDER BY id LIMIT ?", (self._ts(), limit)).fetchall()
            for row in due:
                attempt = row["attempts"] + 1
                delay = self.cfg.smtp.retry_base_seconds * (2 ** (attempt - 1))
                with store.write_tx(conn):
                    claimed = conn.execute(
                        "UPDATE email_outbox SET attempts = ?, next_attempt_at = ? WHERE id = ? AND status = 'pending' "
                        "AND attempts = ?", (attempt, stamp(self.now() + timedelta(seconds=delay)), row["id"],
                                             row["attempts"])).rowcount
                if not claimed:
                    continue
                try:
                    self.sender.send(row["recipient"], row["subject"], row["body"])
                except Exception as exc:  # cualquier fallo de red o SMTP queda registrado, nunca como éxito
                    status = "failed" if attempt >= row["max_attempts"] else "pending"
                    with store.write_tx(conn):
                        conn.execute("UPDATE email_outbox SET status = ?, last_error = ? WHERE id = ?",
                                     (status, clean_text(f"{type(exc).__name__}: {exc}", 300), row["id"]))
                    counts["failed" if status == "failed" else "retry"] += 1
                    continue
                with store.write_tx(conn):
                    conn.execute("UPDATE email_outbox SET status = 'sent', sent_at = ?, last_error = '' WHERE id = ?",
                                 (self._ts(), row["id"]))
                counts["sent"] += 1
            return counts
        finally:
            conn.close()
