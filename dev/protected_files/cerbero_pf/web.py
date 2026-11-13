"""API y páginas servidas por el mismo backend. Cada endpoint sensible comprueba la sesión en cada solicitud."""
from __future__ import annotations

import base64
import sys
import threading
import urllib.parse
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import crypto, geo
from .config import STATIC_DIR
from .service import RequestContext, Service, ServiceError, Session

COOKIE = "cerbero_pf_session"
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' blob:; connect-src 'self'; "
       "form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
SMALL_BODY_LIMIT = 16 * 1024
LARGE_BODY_PATHS = {"/api/documents", "/api/open"}
OPEN_STATUS = {"allowed": 200, "auth_required": 401, "denied": 403, "invalid": 422, "unsupported": 415,
               "rate_limited": 429}


class LoginBody(BaseModel):
    username: str = Field(max_length=64)
    password: str = Field(max_length=256)


class GrantBody(BaseModel):
    username: str = Field(max_length=64)


class StateBody(BaseModel):
    state: str = Field(max_length=16)
    confirm_doc_id: str = Field(max_length=64)


class OutboxWorker(threading.Thread):
    def __init__(self, service: Service):
        super().__init__(daemon=True, name="cerbero-pf-outbox")
        self.service = service
        self.stop_event = threading.Event()

    def run(self) -> None:
        while not self.stop_event.wait(self.service.cfg.smtp.poll_seconds):
            try:
                self.service.process_outbox()
            except Exception as exc:  # la cola sigue persistida; se reintenta en la siguiente vuelta
                print(f"[cola de correo] error: {type(exc).__name__}: {exc}", file=sys.stderr)

    def stop(self) -> None:
        self.stop_event.set()
        self.join(timeout=5)


def _disposition(name: str) -> str:
    fallback = "".join(ch if 32 <= ord(ch) < 127 and ch not in '"\\;' else "_" for ch in name)
    return f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{urllib.parse.quote(name, safe='')}"


def create_app(service: Service, start_worker: bool = True) -> FastAPI:
    cfg = service.cfg
    cookie = "__Host-" + COOKIE if cfg.cookie_secure else COOKIE
    container_limit = cfg.max_plaintext_bytes + crypto.PREFIX.size + crypto.MAX_HEADER_BYTES + crypto.TAG_BYTES

    @asynccontextmanager
    async def lifespan(app):
        worker = OutboxWorker(service) if start_worker and cfg.smtp.enabled else None
        if worker:
            worker.start()
        yield
        if worker:
            worker.stop()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None,
                  telemetry={"tracing": False, "metrics": False, "logs": False, "operation_spans": False,
                             "auto_configure": False})
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(cfg.allowed_hosts))

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = small_body_guard(request) or await call_next(request)
        response.headers["Content-Security-Policy"] = CSP
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), camera=(), microphone=(), usb=()"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"
        return response

    def small_body_guard(request: Request) -> JSONResponse | None:
        """Las rutas con JSON pequeño no leen cuerpos grandes ni sin longitud antes de autenticar."""
        if request.method not in ("POST", "PUT", "PATCH") or request.url.path in LARGE_BODY_PATHS:
            return None
        declared = request.headers.get("content-length")
        if declared is None:
            if request.headers.get("transfer-encoding"):
                return JSONResponse({"result": "error", "code": "length_required",
                                     "message": "Falta Content-Length."}, status_code=411)
            return None
        if not declared.isdigit() or int(declared) > SMALL_BODY_LIMIT:
            return JSONResponse({"result": "error", "code": "too_large",
                                 "message": f"La carga supera el límite de {SMALL_BODY_LIMIT} bytes."}, status_code=413)
        return None

    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        return JSONResponse({"result": "error", "code": exc.code, "message": exc.message}, status_code=exc.status)

    def context(request: Request) -> RequestContext:
        address = geo.client_address(request.client.host if request.client else None,
                                     request.headers.get("x-forwarded-for"), cfg.trusted_proxies)
        return RequestContext(ip=address.ip, ip_source=address.source, forwarded_header=address.forwarded_raw,
                              user_agent=request.headers.get("user-agent", ""),
                              client_location_raw=request.headers.get("x-client-location"))

    def check_origin(request: Request) -> None:
        origin = request.headers.get("origin")
        allowed = {str(request.base_url).rstrip("/"), cfg.public_base_url.rstrip("/")} - {""}
        if origin and origin.rstrip("/") not in allowed:
            raise ServiceError(403, "bad_origin", "Origen no permitido.")

    def require(request: Request, csrf: bool = False) -> Session:
        session = service.session(request.cookies.get(cookie))
        if session is None:
            raise ServiceError(401, "auth_required", "Inicia sesión para continuar.")
        if csrf:
            check_origin(request)
            if not service.csrf_ok(session, request.headers.get("x-csrf-token")):
                raise ServiceError(403, "csrf", "Falta el token CSRF o no coincide con la sesión.")
        return session

    async def read_limited(request: Request, limit: int) -> bytes:
        declared = request.headers.get("content-length")
        if declared is not None and (not declared.isdigit() or int(declared) > limit):
            raise ServiceError(413, "too_large", f"La carga supera el límite de {limit} bytes.")
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > limit:
                raise ServiceError(413, "too_large", f"La carga supera el límite de {limit} bytes.")
        return bytes(body)

    def user_json(session: Session) -> dict:
        return {"user": {"username": session.username, "display_name": session.display_name},
                "csrf_token": session.csrf_token, "limits": {"max_plaintext_bytes": cfg.max_plaintext_bytes}}

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse("/panel", status_code=303)

    @app.get("/panel", include_in_schema=False)
    def panel():
        return FileResponse(STATIC_DIR / "panel.html", headers={"Cache-Control": "no-store"})

    @app.get("/visor", include_in_schema=False)
    def viewer():
        return FileResponse(STATIC_DIR / "visor.html", headers={"Cache-Control": "no-store"})

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/login")
    def login(request: Request, body: LoginBody):
        check_origin(request)
        token, session = service.login(body.username, body.password, context(request).ip)
        response = JSONResponse(user_json(session))
        response.set_cookie(cookie, token, max_age=int(cfg.session_hours * 3600), path="/", httponly=True,
                            samesite="strict", secure=cfg.cookie_secure)
        return response

    @app.post("/api/logout")
    def logout(request: Request):
        service.logout(require(request, csrf=True))
        response = JSONResponse({"result": "ok"})
        response.delete_cookie(cookie, path="/", httponly=True, samesite="strict", secure=cfg.cookie_secure)
        return response

    @app.get("/api/me")
    def me(request: Request):
        return user_json(require(request))

    @app.post("/api/documents", status_code=201)
    async def export(request: Request):
        session = await run_in_threadpool(require, request, True)
        data = await read_limited(request, cfg.max_plaintext_bytes)
        name = urllib.parse.unquote(request.headers.get("x-filename", "")[:1024], errors="replace")
        doc, _ = await run_in_threadpool(service.export_document, session, name, data, context(request))
        return JSONResponse({"document": doc, "container_url": f"/api/documents/{doc['id']}/container"},
                            status_code=201)

    @app.get("/api/documents")
    def documents(request: Request):
        return {"documents": service.list_documents(require(request))}

    @app.get("/api/documents/{doc_id}")
    def document(request: Request, doc_id: str):
        return {"document": service.get_document(require(request), doc_id)}

    @app.get("/api/documents/{doc_id}/container")
    def container(request: Request, doc_id: str):
        name, data = service.container_bytes(require(request), doc_id)
        return Response(data, media_type="application/octet-stream", headers={"Content-Disposition": _disposition(name)})

    @app.post("/api/documents/{doc_id}/grants")
    def add_grant(request: Request, doc_id: str, body: GrantBody):
        session = require(request, csrf=True)
        return {"document": service.set_grant(session, doc_id, body.username, True, context(request))}

    @app.post("/api/documents/{doc_id}/grants/revoke")
    def revoke_grant(request: Request, doc_id: str, body: GrantBody):
        session = require(request, csrf=True)
        return {"document": service.set_grant(session, doc_id, body.username, False, context(request))}

    @app.post("/api/documents/{doc_id}/state")
    def set_state(request: Request, doc_id: str, body: StateBody):
        session = require(request, csrf=True)
        return {"document": service.set_state(session, doc_id, body.state, body.confirm_doc_id, context(request))}

    @app.get("/api/documents/{doc_id}/audit")
    def audit(request: Request, doc_id: str):
        record = service.audit_export(require(request), doc_id)
        return JSONResponse(record, headers={"Content-Disposition": _disposition(f"cerbero-pf-audit-{doc_id}.json")})

    @app.get("/api/events")
    def events(request: Request, doc_id: str | None = None):
        return {"events": service.events(require(request), doc_id)}

    @app.get("/api/telemetry")
    def telemetry(request: Request):
        return {"events": service.telemetry(require(request))}

    @app.get("/api/notifications")
    def notifications(request: Request):
        return {"notifications": service.notifications(require(request))}

    @app.post("/api/notifications/{notification_id}/read")
    def mark_read(request: Request, notification_id: int):
        service.mark_read(require(request, csrf=True), notification_id)
        return {"result": "ok"}

    @app.post("/api/open")
    async def open_container(request: Request):
        token = request.cookies.get(cookie)
        session = await run_in_threadpool(service.session, token) if token else None
        if session is not None:
            check_origin(request)
            if not service.csrf_ok(session, request.headers.get("x-csrf-token")):
                raise ServiceError(403, "csrf", "Falta el token CSRF o no coincide con la sesión.")
        data = await read_limited(request, container_limit)
        result = await run_in_threadpool(service.open_container, data, session, context(request))
        payload = {"result": result.result, "reason": result.reason, "message": result.message,
                   "event_id": result.event_id, "document": result.document}
        if result.content is not None:
            payload["content_b64"] = base64.b64encode(result.content).decode("ascii")
        return JSONResponse(payload, status_code=OPEN_STATUS[result.result])

    return app
