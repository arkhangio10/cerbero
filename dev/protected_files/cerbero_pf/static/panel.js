"use strict";

(() => {
  const { api, el, utc, kinds, reasons, clientLocationText, ipText } = Cerbero;
  const $ = (id) => document.getElementById(id);
  const stateText = { active: "Activo", lost: "Extraviado", revoked: "Revocado" };
  let pendingConfirm = null;

  function say(node, text, kind) {
    node.textContent = text;
    node.dataset.kind = kind || "";
  }

  function bytes(n) {
    return n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(1)} KiB` : `${(n / 1048576).toFixed(2)} MiB`;
  }

  async function show(user, limits) {
    $("login-view").classList.toggle("hidden", Boolean(user));
    $("app-view").classList.toggle("hidden", !user);
    $("logout").classList.toggle("hidden", !user);
    $("who").classList.toggle("hidden", !user);
    if (!user) return;
    $("who").textContent = `Sesión: ${user.display_name} (${user.username})`;
    if (limits) $("limit").textContent = bytes(limits.max_plaintext_bytes);
    await refresh();
  }

  async function refresh() {
    const [docs, notes, events, telemetry] = await Promise.all([
      api("/api/documents"), api("/api/notifications"), api("/api/events"), api("/api/telemetry"),
    ]);
    if (docs.status === 401) return show(null);
    renderDocs(docs.data.documents);
    renderAlerts(notes.data.notifications);
    renderEvents(events.data.events);
    renderTelemetry(telemetry.data.events);
  }

  function download(blob, name) {
    const url = URL.createObjectURL(blob);
    const link = el("a", { href: url, download: name });
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function downloadContainer(doc) {
    const response = await fetch(`/api/documents/${encodeURIComponent(doc.id)}/container`, { credentials: "same-origin", cache: "no-store" });
    if (!response.ok) throw new Error(`No se pudo descargar el contenedor (${response.status}).`);
    download(await response.blob(), doc.container_name);
  }

  async function downloadAudit(doc) {
    const r = await api(`/api/documents/${encodeURIComponent(doc.id)}/audit`);
    if (r.ok) download(new Blob([JSON.stringify(r.data, null, 2)], { type: "application/json" }), `cerbero-pf-audit-${doc.id}.json`);
  }

  function renderDocs(docs) {
    const list = $("docs");
    list.replaceChildren();
    if (!docs.length) {
      list.append(el("li", { class: "empty", text: "Aún no has exportado ningún archivo. Elige uno arriba para crear su copia cifrada." }));
      return;
    }
    for (const doc of docs) list.append(renderDoc(doc));
  }

  function renderDoc(doc) {
    const msg = el("p", { class: "message", role: "status" });
    const item = el("li", { class: "doc", "data-state": doc.state, "data-doc": doc.id });
    const active = doc.state === "active";

    const grants = el("ul", { class: "grants" });
    const current = doc.grants.filter((g) => !g.revoked_at);
    if (!doc.grants.length) grants.append(el("li", { class: "empty", text: "Nadie más tiene acceso." }));
    for (const g of doc.grants) {
      const revokeGrant = active && !g.revoked_at
        ? el("button", { class: "quiet", type: "button", onclick: () => changeGrant(doc, g.username, false, msg) }, `Quitar acceso a ${g.username}`)
        : null;
      grants.append(el("li", {},
        el("span", { class: g.revoked_at ? "revoked-grant" : "" }, g.username),
        el("span", { class: "meta" }, g.revoked_at ? `permiso revocado ${utc(g.revoked_at)}` : `desde ${utc(g.granted_at)}`),
        revokeGrant));
    }

    const grantInput = el("input", { type: "text", id: `grant-${doc.id}`, autocomplete: "off", placeholder: "usuario" });
    const grantForm = active ? el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); changeGrant(doc, grantInput.value.trim(), true, msg); } },
      el("div", { class: "field" }, el("label", { for: `grant-${doc.id}` }, "Dar acceso de lectura a"), grantInput),
      el("button", { type: "submit", class: "secondary" }, "Dar acceso")) : null;

    const confirmBox = el("div", { class: "confirm hidden" });
    const askState = (state) => () => {
      pendingConfirm = { id: doc.id, state };
      confirmBox.dataset.state = state;
      const label = state === "lost" ? "Marcar como extraviado" : "Revocar documento";
      confirmBox.replaceChildren(
        el("p", {}, state === "lost"
          ? "Las nuevas solicitudes de contenido se denegarán, también desde sesiones ya abiertas y desde cualquier copia de este archivo. Cada intento quedará registrado y te avisará."
          : "Revocar es definitivo: nadie, ni tú, podrá volver a abrir este contenedor ni sus copias."),
        el("p", {}, "Lo que ya se entregó antes no se puede retirar."),
        el("div", { class: "actions" },
          el("button", { type: "button", class: state === "lost" ? "warn" : "danger", onclick: () => applyState(doc, state, msg) }, `Confirmar: ${label.toLowerCase()}`),
          el("button", { type: "button", class: "secondary", onclick: () => { pendingConfirm = null; confirmBox.classList.add("hidden"); } }, "Cancelar")));
      confirmBox.classList.remove("hidden");
    };

    item.append(...[
      el("div", { class: "doc-head" },
        el("h3", { class: "doc-name" }, doc.display_name),
        el("span", { class: "seal" }, stateText[doc.state])),
      el("dl", { class: "facts" },
        el("dt", {}, "Contenedor"), el("dd", {}, doc.container_name),
        el("dt", {}, "Tamaño"), el("dd", {}, `${bytes(doc.size)}, ${doc.media_type.startsWith("text/") || doc.media_type.startsWith("image/") ? "visible en el visor" : "no se muestra en el visor"}`),
        el("dt", {}, "Exportado"), el("dd", {}, utc(doc.created_at)),
        doc.state_changed_at ? [el("dt", {}, "Efectivo desde"), el("dd", {}, utc(doc.state_changed_at))] : null,
        el("dt", {}, "ID"), el("dd", { class: "code" }, doc.id),
        el("dt", {}, "SHA-256"), el("dd", { class: "code" }, doc.container_sha256)),
      el("h3", {}, current.length ? "Pueden leerlo" : "Permisos"),
      grants,
      grantForm,
      el("div", { class: "actions" },
        el("button", { type: "button", class: "secondary", onclick: () => downloadContainer(doc).catch((e) => say(msg, e.message, "error")) }, "Descargar .cerbero"),
        el("button", { type: "button", class: "secondary", onclick: () => downloadAudit(doc) }, "Exportar registro"),
        active ? el("button", { type: "button", class: "warn", onclick: askState("lost") }, "Marcar como extraviado") : null,
        doc.state !== "revoked" ? el("button", { type: "button", class: "danger", onclick: askState("revoked") }, "Revocar documento") : null),
      confirmBox,
      msg].filter(Boolean));
    return item;
  }

  async function changeGrant(doc, username, allow, msg) {
    if (!username) return say(msg, "Escribe el usuario.", "error");
    const r = await api(`/api/documents/${encodeURIComponent(doc.id)}/grants${allow ? "" : "/revoke"}`, { method: "POST", body: { username } });
    if (!r.ok) return say(msg, r.data?.message || `Error ${r.status}.`, "error");
    await refresh();
  }

  async function applyState(doc, state, msg) {
    if (!pendingConfirm || pendingConfirm.id !== doc.id || pendingConfirm.state !== state) return;
    pendingConfirm = null;
    const r = await api(`/api/documents/${encodeURIComponent(doc.id)}/state`, { method: "POST", body: { state, confirm_doc_id: doc.id } });
    if (!r.ok) return say(msg, r.data?.message || `Error ${r.status}.`, "error");
    await refresh();
    const node = document.querySelector(`[data-doc="${CSS.escape(doc.id)}"] .message`);
    if (node) say(node, `Guardado. Efectivo desde ${utc(r.data.document.effective_at)}: las solicitudes nuevas se deniegan.`, "ok");
  }

  function mailText(n) {
    if (n.email_state === "disabled") return { status: "off", text: "Correo desactivado: SMTP no configurado." };
    if (n.email_state === "no_recipient") return { status: "off", text: "Sin correo de destino en tu cuenta." };
    if (n.email_state === "burst_skipped") return { status: "off", text: "Correo omitido por el límite de avisos por hora." };
    if (n.email_status === "sent") return { status: "sent", text: `Correo enviado: el servidor SMTP lo aceptó (${utc(n.email_sent_at)}).` };
    if (n.email_status === "failed") return { status: "failed", text: `Correo fallido tras ${n.email_attempts} intentos: ${n.email_error}` };
    const error = n.email_error ? ` Último error: ${n.email_error}` : "";
    return { status: "pending", text: `Correo pendiente (${n.email_attempts} de ${n.email_max} intentos).${error}` };
  }

  function renderAlerts(notes) {
    const list = $("alerts");
    list.replaceChildren();
    if (!notes.length) {
      list.append(el("li", { class: "empty", text: "Sin avisos. Aparecerán aquí los intentos denegados sobre tus documentos." }));
      return;
    }
    for (const n of notes) {
      const mail = mailText(n);
      list.append(el("li", { class: "alert", "data-read": String(Boolean(n.read_at)) },
        el("h3", {}, n.title),
        el("p", {}, n.body),
        el("p", { class: "meta" }, n.count > 1 ? `${n.count} intentos agrupados, del ${utc(n.first_at)} al ${utc(n.last_at)}` : utc(n.first_at)),
        el("p", { class: "meta mail", "data-status": mail.status }, mail.text),
        n.read_at ? null : el("button", { class: "quiet", type: "button", onclick: async () => { await api(`/api/notifications/${n.id}/read`, { method: "POST" }); refresh(); } }, "Marcar como leído")));
    }
  }

  function renderEvents(events) {
    const body = $("events");
    body.replaceChildren();
    if (!events.length) {
      body.append(el("tr", {}, el("td", { colspan: "8", class: "empty" }, "Sin actividad registrada.")));
      return;
    }
    for (const e of events) {
      body.append(el("tr", { "data-result": e.result },
        el("td", { class: "when" }, utc(e.at_utc)),
        el("td", {}, kinds[e.kind] || e.kind),
        el("td", {}, e.container_name || "—"),
        el("td", {}, e.actor_label),
        el("td", {}, [reasons[e.reason] || e.reason, e.detail ? ` (${e.detail})` : ""].join("")),
        el("td", {}, ipText(e)),
        el("td", {}, e.geo && e.geo.status ? e.geo_text : "—"),
        el("td", {}, clientLocationText(e.client_location))));
    }
  }

  function renderTelemetry(events) {
    const body = $("telemetry");
    body.replaceChildren();
    if (!events.length) {
      body.append(el("tr", {}, el("td", { colspan: "5", class: "empty" }, "Nada que mostrar.")));
      return;
    }
    for (const e of events) {
      body.append(el("tr", { "data-result": e.result },
        el("td", { class: "when" }, utc(e.at_utc)),
        el("td", { class: "code" }, e.claimed_doc_id || "—"),
        el("td", {}, reasons[e.reason] || e.reason),
        el("td", {}, e.actor_label),
        el("td", {}, ipText(e))));
    }
  }

  async function exportFile(event) {
    event.preventDefault();
    const file = $("export-file").files[0];
    const msg = $("export-msg");
    if (!file) return;
    say(msg, "Cifrando…");
    const r = await api("/api/documents", { method: "POST", body: file, headers: { "Content-Type": "application/octet-stream", "X-Filename": encodeURIComponent(file.name) } });
    if (!r.ok) return say(msg, r.data?.message || `Error ${r.status}.`, "error");
    const doc = r.data.document;
    await downloadContainer(doc);
    say(msg, `Exportado: ${doc.container_name} se descargó. El archivo original no se modificó.`, "ok");
    $("export-form").reset();
    await refresh();
  }

  async function init() {
    $("login-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const r = await Cerbero.login($("login-user").value.trim(), $("login-pass").value);
      if (!r.ok) return say($("login-msg"), r.data?.message || "No se pudo iniciar sesión.", "error");
      $("login-form").reset();
      show(r.data.user, r.data.limits);
    });
    $("logout").addEventListener("click", async () => { await Cerbero.logout(); show(null); });
    $("export-form").addEventListener("submit", (e) => exportFile(e).catch((err) => say($("export-msg"), err.message, "error")));
    $("refresh").addEventListener("click", refresh);
    setInterval(() => { if (!$("app-view").classList.contains("hidden")) refresh().catch(() => {}); }, 15000);
    try {
      const r = await api("/api/me");
      if (r.ok) {
        await Cerbero.me();
        show(r.data.user, r.data.limits);
      } else {
        show(null);
      }
    } catch {
      $("login-view").classList.remove("hidden");
      say($("login-msg"), "Servicio no disponible.", "error");
    }
  }

  init();
})();
