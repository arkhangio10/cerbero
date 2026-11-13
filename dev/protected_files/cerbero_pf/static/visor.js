"use strict";

(() => {
  const { el } = Cerbero;
  const $ = (id) => document.getElementById(id);
  let user = null;
  let clientLocation = null;
  let objectUrl = null;

  const titles = {
    auth: "Autorización requerida",
    allowed: "Acceso permitido",
    denied: "Acceso denegado",
    lost: "Documento extraviado",
    revoked: "Documento revocado",
    invalid: "Archivo inválido",
    unsupported: "Formato no soportado",
    limited: "Demasiados intentos",
    unavailable: "Servicio no disponible",
  };

  function status(state, text) {
    const box = $("status");
    box.dataset.state = state;
    box.classList.remove("hidden");
    $("status-title").textContent = titles[state];
    $("status-text").textContent = text;
  }

  function clearContent() {
    $("content").replaceChildren();
    if (objectUrl) URL.revokeObjectURL(objectUrl);
    objectUrl = null;
  }

  function setUser(next) {
    user = next;
    $("who").classList.toggle("hidden", !user);
    $("logout").classList.toggle("hidden", !user);
    $("who").textContent = user ? `Sesión: ${user.display_name} (${user.username})` : "";
  }

  function decode(b64) {
    const raw = atob(b64);
    const out = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i += 1) out[i] = raw.charCodeAt(i);
    return out;
  }

  function render(doc, b64) {
    clearContent();
    const data = decode(b64);
    const box = $("content");
    box.append(el("h3", {}, doc.name));
    if (doc.media_type.startsWith("text/plain")) {
      box.append(el("pre", {}, new TextDecoder("utf-8", { fatal: true }).decode(data)));
    } else {
      objectUrl = URL.createObjectURL(new Blob([data], { type: doc.media_type }));
      box.append(el("img", { src: objectUrl, alt: `Imagen protegida: ${doc.name}` }));
    }
    box.append(el("p", { class: "lede" }, "Este visor no impide capturas de pantalla ni copias de lo que ya ves. Si el propietario revoca el documento después, lo ya entregado no se puede retirar."));
  }

  async function openContainer() {
    const file = $("container").files[0];
    if (!file) return;
    clearContent();
    const headers = { "Content-Type": "application/octet-stream" };
    if (clientLocation) headers["X-Client-Location"] = JSON.stringify(clientLocation);
    let r;
    try {
      r = await Cerbero.api("/api/open", { method: "POST", body: file, headers });
    } catch {
      status("unavailable", "No hay conexión con el servicio. Sin conexión no se concede una nueva apertura ni se registra el intento.");
      return;
    }
    const data = r.data || {};
    $("login-form").classList.add("hidden");
    if (r.status === 200) {
      status("allowed", data.message);
      render(data.document, data.content_b64);
    } else if (r.status === 401 && data.result === "auth_required") {
      status("auth", data.message);
      $("login-form").classList.remove("hidden");
      $("login-user").focus();
    } else if (r.status === 403 && data.reason === "document_lost") {
      status("lost", data.message);
    } else if (r.status === 403 && data.reason === "document_revoked") {
      status("revoked", data.message);
    } else if (r.status === 403 && data.result === "denied") {
      status("denied", data.message);
    } else if (r.status === 422) {
      status("invalid", data.message || "El archivo no es un contenedor válido.");
    } else if (r.status === 413) {
      status("invalid", data.message || "El archivo supera el tamaño admitido.");
    } else if (r.status === 415) {
      status("unsupported", data.message);
    } else if (r.status === 429) {
      status("limited", data.message);
    } else if (r.status === 403) {
      status("denied", data.message || "Solicitud rechazada.");
    } else {
      status("unavailable", data.message || `El servicio respondió ${r.status}. No se entrega contenido.`);
    }
  }

  function shareLocation() {
    const msg = $("location-msg");
    if (!("geolocation" in navigator)) {
      clientLocation = { status: "unavailable" };
      msg.textContent = "Este navegador no ofrece ubicación. Se registrará que no estuvo disponible.";
      return;
    }
    msg.textContent = "Esperando la respuesta del navegador…";
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        clientLocation = { status: "granted", lat: pos.coords.latitude, lon: pos.coords.longitude, accuracy_m: pos.coords.accuracy, timestamp_ms: pos.timestamp };
        msg.textContent = `Se enviará con cada apertura desde esta página hasta que pulses «No compartir»: ${pos.coords.latitude.toFixed(3)}, ${pos.coords.longitude.toFixed(3)} (±${Math.round(pos.coords.accuracy)} m).`;
      },
      (err) => {
        clientLocation = { status: err.code === 1 ? "denied" : "unavailable" };
        msg.textContent = err.code === 1
          ? "Permiso denegado. Se registrará la negativa; tus permisos de lectura no cambian."
          : "El navegador no obtuvo la ubicación. Se registrará que no estuvo disponible.";
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 0 });
  }

  async function init() {
    $("open-form").addEventListener("submit", (e) => { e.preventDefault(); openContainer(); });
    $("clear").addEventListener("click", () => { clearContent(); $("status").classList.add("hidden"); });
    $("share-location").addEventListener("click", shareLocation);
    $("forget-location").addEventListener("click", () => { clientLocation = null; $("location-msg").textContent = "No se compartirá ninguna ubicación."; });
    $("logout").addEventListener("click", async () => { await Cerbero.logout(); setUser(null); clearContent(); });
    $("login-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      let r;
      try {
        r = await Cerbero.login($("login-user").value.trim(), $("login-pass").value);
      } catch {
        status("unavailable", "No hay conexión con el servicio.");
        return;
      }
      if (!r.ok) {
        $("login-msg").textContent = r.data?.message || "No se pudo iniciar sesión.";
        $("login-msg").dataset.kind = "error";
        return;
      }
      $("login-form").reset();
      $("login-msg").textContent = "";
      setUser(r.data.user);
      await openContainer();
    });
    try {
      setUser(await Cerbero.me());
    } catch {
      status("unavailable", "No hay conexión con el servicio. Sin conexión no se puede abrir ningún archivo protegido.");
    }
  }

  init();
})();
