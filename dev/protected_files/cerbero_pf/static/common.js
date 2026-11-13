"use strict";

// Utilidades compartidas. Todo texto recibido se inserta con textContent; nunca se interpreta como HTML.
const Cerbero = (() => {
  let csrf = null;

  async function api(path, { method = "GET", body, headers = {} } = {}) {
    const sent = { ...headers };
    let payload = body;
    if (csrf && method !== "GET") sent["X-CSRF-Token"] = csrf;
    if (body !== undefined && !(body instanceof Blob)) {
      sent["Content-Type"] = "application/json";
      payload = JSON.stringify(body);
    }
    const response = await fetch(path, { method, body: payload, headers: sent, credentials: "same-origin", cache: "no-store" });
    let data = null;
    try { data = await response.json(); } catch { data = null; }
    return { status: response.status, ok: response.ok, data };
  }

  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (value === null || value === undefined || value === false) continue;
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
      else node.setAttribute(key, value === true ? "" : value);
    }
    for (const child of children.flat()) {
      if (child === null || child === undefined || child === false) continue;
      node.append(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return node;
  }

  function utc(stamp) {
    if (!stamp) return "—";
    return stamp.replace("T", " ").replace(/(\.\d+)?Z$/, " UTC");
  }

  async function me() {
    const r = await api("/api/me");
    csrf = r.ok ? r.data.csrf_token : null;
    return r.ok ? r.data.user : null;
  }

  async function login(username, password) {
    const r = await api("/api/login", { method: "POST", body: { username, password } });
    if (r.ok) csrf = r.data.csrf_token;
    return r;
  }

  async function logout() {
    await api("/api/logout", { method: "POST" });
    csrf = null;
  }

  const kinds = {
    export: "Exportación",
    permission_change: "Cambio de permisos",
    revocation: "Revocación o extravío",
    access_request: "Solicitud de acceso",
    access_denied: "Acceso denegado",
    content_served: "Contenido entregado al visor",
    container_invalid: "Contenedor inválido",
    integrity_failure: "Comprobación de integridad fallida",
  };

  const reasons = {
    exported: "exportado",
    grant_added: "permiso concedido",
    grant_revoked: "permiso revocado",
    marked_lost: "marcado como extraviado",
    revoked: "documento revocado",
    authentication_required: "autorización requerida",
    document_lost: "documento extraviado",
    document_revoked: "documento revocado",
    no_permission: "cuenta sin permiso",
    unsupported_format: "formato no soportado",
    integrity_failure: "integridad no comprobada",
    authorized_owner: "propietario autorizado",
    authorized_reader: "lector autorizado",
    unknown_document: "no corresponde a ningún documento",
    does_not_match_registered_export: "no coincide con la exportación registrada",
    truncated: "archivo truncado",
    bad_magic: "no es un contenedor .cerbero",
    unknown_version: "versión desconocida",
    bad_header: "cabecera inválida",
    size_mismatch: "tamaño incoherente",
  };

  function clientLocationText(loc) {
    if (!loc || loc.status === "not_requested") return "no solicitada";
    if (loc.status === "denied") return "permiso denegado por el navegador";
    if (loc.status === "unavailable") return "el navegador no la obtuvo";
    if (loc.status === "invalid") return "datos inválidos, descartados";
    return `declarada por el navegador: ${loc.lat.toFixed(3)}, ${loc.lon.toFixed(3)} (±${Math.round(loc.accuracy_m)} m; no verificada)`;
  }

  function ipText(event) {
    const forwarded = event.forwarded_header && event.ip_source === "conexión" ? "; X-Forwarded-For ignorado" : "";
    return `${event.ip} (${event.ip_source}${forwarded})`;
  }

  return { api, el, utc, me, login, logout, kinds, reasons, clientLocationText, ipText };
})();
