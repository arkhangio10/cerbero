# Cerbero: archivos protegidos (prototipo local)

Servicio complementario de desarrollo para **exportación cifrada, acceso controlado, alertas y revocación**. Es independiente de la Skill `cerbero-guardian`: no forma parte del ZIP, la Skill no lo llama y no cambia sus reglas de recuperación ni de aprobación. La integración con la Skill es, por ahora, documental: el panel exporta un registro JSON por documento para revisarlo a mano.

Estado (12 de noviembre de 2026): funciona en Windows 11 con Python 3.11.9, sólo en loopback y con datos sintéticos. No se ha ejecutado en un NAS UGREEN ni en UGOS.

## Qué hace

1. La persona propietaria elige un archivo y obtiene una copia cifrada `.cerbero`. El original no se toca. Sólo quedan protegidas las exportaciones hechas por este flujo: el servicio no intercepta otras copias ni salidas de archivos.
2. Quien recibe el `.cerbero` lo carga en el visor web (`/visor`). El visor avisa de que el acceso se registra y pide iniciar sesión. El servidor comprueba identidad, permiso, integridad y estado del documento antes de descifrar.
3. La persona propietaria puede marcar el documento como extraviado o revocarlo. Desde que esa operación se confirma en la base de datos, toda solicitud nueva de contenido se deniega: también las de sesiones abiertas antes y las de cualquier copia del mismo contenedor.
4. Cada intento sospechoso (documento extraviado o revocado, cuenta sin permiso o con el permiso retirado, fallo de integridad) deja un evento persistente y un aviso en el panel, más un correo opcional por SMTP. Las aperturas autorizadas también quedan auditadas.

Un evento «contenido entregado» significa que el servidor envió el contenido al visor. No prueba que una persona lo leyera, y un intento no equivale a una lectura ni a un robo.

## Límites que no se deben olvidar

- **Sin rastreo fuera del visor.** Un archivo pasivo no transmite su ubicación. El servicio sólo ve las solicitudes que le llegan.
- **Sin detección de descifrado externo.** Si alguien rompe el cifrado fuera del servicio, no se entera nadie. Para AES-256-GCM eso exige la clave, que nunca sale del servidor.
- **Sin conexión no hay apertura nueva ni alerta inmediata.**
- **La ubicación no demuestra identidad.** La de IP es aproximada y puede ser la de una VPN. La del navegador la declara el cliente y se puede falsear.
- **Revocar no borra lo ya entregado.** Las respuestas llevan `Cache-Control: no-store`, pero nada impide capturas de pantalla ni copias de lo que ya se vio.
- **No protege frente al compromiso completo del servidor.** Quien controle el proceso, la clave maestra y la base de datos puede descifrarlo todo. El cifrado en reposo, los registros locales y estas pruebas de laboratorio no cambian eso.
- **Perder el servicio o sus claves puede hacer irrecuperables estas exportaciones.** No hay depósito de claves.
- **Integración con UGOS pendiente.** No hay comandos UGOS para este servicio, y la Skill no lo consume automáticamente.
- Sin macros, ejecutables ocultos, balizas encubiertas ni permisos de ubicación eludidos.

## Instalación (Windows, PowerShell)

Desde la raíz del repositorio:

```powershell
cd dev\protected_files
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` fija todas las versiones: FastAPI 0.162.5, Starlette 1.10.0, uvicorn 0.54.0, cryptography 50.0.2, aiosmtpd 1.4.6, httpx 0.28.1 y sus dependencias. Se verificaron con Python 3.11.9 el 12 de noviembre de 2026. No hace falta activar el entorno: todos los comandos usan `.\.venv\Scripts\python.exe`.

La prueba de navegador es opcional y necesita Playwright:

```powershell
.\.venv\Scripts\python.exe -m pip install playwright==1.58.0
.\.venv\Scripts\python.exe -m playwright install chromium
```

Sin Playwright, esa prueba se informa como omitida, no como aprobada.

## Demo reproducible

```powershell
.\.venv\Scripts\python.exe -m cerbero_pf demo --fresh
```

La demo crea sólo datos sintéticos en `dev\out\protected_files_demo\`: una clave maestra nueva, tres cuentas con contraseñas aleatorias y un `Contrato.txt` ficticio. Arranca el servicio en otro proceso, en un puerto libre de `127.0.0.1`, y un buzón SMTP local. Después hace estos pasos y comprueba cada uno:

1. Exporta `Contrato.txt` a `Contrato.cerbero` y verifica que el SHA-256 y la fecha de modificación del original no cambian.
2. La cuenta `lector` lo abre y recibe exactamente los bytes originales. La propietaria ve el evento real, con hora UTC, IP y «ubicación no disponible».
3. La propietaria lo marca como extraviado. Se muestra el instante desde el que la marca es efectiva.
4. La cuenta `tercero` abre una copia del contenedor desde otra sesión y recibe una denegación. La sesión anterior del lector también queda denegada. Se generan el evento y el aviso.
5. El correo llega al buzón local y la cola lo marca «enviado» sólo después de que el servidor SMTP lo acepte.
6. La demo detiene el servicio por la fuerza: sin servicio no se puede abrir nada. Al arrancarlo de nuevo, el estado extraviado, los eventos y la denegación de la sesión anterior siguen ahí.

Resultado de referencia: 15/15 comprobaciones correctas, o 16/16 con `--geo-simulado`. La salida queda en `demo-transcript.txt` y `demo-summary.json`; el correo, en `mailbox\*.eml`; el registro del servidor, en `server.log`.

Opciones:

- `--keep-running`: deja el servicio y el buzón activos para probar el panel y el visor en el navegador. Imprime la URL; las contraseñas sintéticas están en `credentials.txt`. Ctrl+C lo detiene.
- `--geo-simulado`: añade un caso aparte con un proveedor geográfico simulado, para enseñar el aspecto de la alerta. Todo resultado lleva la marca «SIMULADO». En localhost la ubicación real siempre es «no disponible».
- `--fresh`: reemplaza una demo anterior. Sólo borra una carpeta que tenga la marca `.cerbero-pf-demo`.

Para ver los correos del buzón de la demo:

```powershell
.\.venv\Scripts\python.exe -m cerbero_pf mailbox --dir ..\out\protected_files_demo\mailbox --list
```

## Uso manual

```powershell
Copy-Item config.example.toml config.local.toml
New-Item -ItemType Directory -Force ..\out\protected_files\nas | Out-Null
.\.venv\Scripts\python.exe -m cerbero_pf genkey --config config.local.toml
.\.venv\Scripts\python.exe -m cerbero_pf create-user --config config.local.toml propietario --email propietario@demo.invalid
.\.venv\Scripts\python.exe -m cerbero_pf create-user --config config.local.toml lector
.\.venv\Scripts\python.exe -m cerbero_pf create-user --config config.local.toml tercero
.\.venv\Scripts\python.exe -m cerbero_pf serve --config config.local.toml
```

`create-user` imprime una contraseña aleatoria una sola vez. Para fijarla localmente, usa `--password-env NOMBRE_DE_VARIABLE`, con al menos 12 caracteres. Después abre `http://127.0.0.1:8765/panel` (propietaria) y `http://127.0.0.1:8765/visor` (lector).

Correo de prueba. Abre otra ventana de PowerShell en `dev\protected_files`, pon `enabled = true` en la sección `[smtp]` de `config.local.toml` y reinicia `serve`:

```powershell
.\.venv\Scripts\python.exe -m cerbero_pf mailbox --dir ..\out\protected_files\mailbox --port 8025
```

Exportación por ruta: es el equivalente local a elegir un archivo de una carpeta del NAS. Sólo admite archivos dentro de `export_roots`:

```powershell
.\.venv\Scripts\python.exe -m cerbero_pf export --config config.local.toml --owner propietario ..\out\protected_files\nas\Contrato.txt
```

Si no puedes iniciar sesión en el panel (por ejemplo, porque alguien agotó los intentos de tu cuenta), quien controla la configuración y la clave maestra puede marcar o revocar desde la línea de órdenes. El ID aparece en el panel y en el registro exportado:

```powershell
.\.venv\Scripts\python.exe -m cerbero_pf set-state --config config.local.toml --owner propietario <ID_DEL_DOCUMENTO> lost
```

## Configuración

`config.example.toml` documenta cada opción y no contiene secretos. Puntos clave:

- `server.host` debe ser loopback. Otra dirección exige `allow_non_loopback = true`, y un despliegue fuera del equipo requiere HTTPS (`cookie_secure = true`) y una configuración de seguridad revisada. No se abren puertos públicos.
- `storage.master_key_file` es obligatorio y no puede estar dentro de `data_dir` ni del directorio público `cerbero_pf\static`.
- Detrás de un proxy HTTPS, `server.public_base_url` (por ejemplo `https://nas.local`) es el origen admitido para las acciones del panel, además del propio. Añade también ese nombre a `allowed_hosts`.
- `server.trusted_proxies` está vacío por defecto: `X-Forwarded-For` se registra como dato recibido, pero se ignora. Uvicorn se arranca con `proxy_headers=False`.
- `geo.provider = "none"` por defecto: nunca se envía una IP ni un documento a proveedores externos. `csv` usa una base local (`network,country,region,city,accuracy_radius_km`, por ejemplo derivada de GeoLite2 respetando su licencia). `simulated` es sólo para la demo.
- `smtp.enabled = false` por defecto. Un servidor que no sea loopback exige `allow_external = true`. La contraseña se lee de `CERBERO_PF_SMTP_PASSWORD`, nunca del archivo.
- Límites: 1 MiB por archivo (máximo configurable: 8 MiB), 5 fallos de inicio de sesión por usuario o IP en 15 minutos, 30 aperturas por IP y minuto, sesiones de 8 horas y 10 correos por hora y propietaria.

## Formato del contenedor `.cerbero` (versión 1)

| Campo | Tamaño | Contenido |
|---|---|---|
| magia | 7 bytes | `CERBERO` |
| versión | 1 byte | `1`; cualquier otra se rechaza |
| longitud de cabecera | 4 bytes, big-endian | 1 a 1024 |
| cabecera | variable | JSON canónico ASCII (claves ordenadas, sin espacios) con exactamente `alg` (`AES-256-GCM`), `created`, `doc` (ID opaco `pf_` + 24 caracteres aleatorios), `len` (bytes del original) y `nonce` (12 bytes, base64url), más `v` |
| texto cifrado | `len` + 16 bytes | AES-256-GCM con etiqueta de 16 bytes |

- **Datos autenticados (AAD):** todos los bytes anteriores al texto cifrado. Cambiar la versión, el ID, la fecha, el nonce o la longitud invalida la etiqueta.
- **Una clave por exportación:** 32 bytes aleatorios. Como cada clave cifra un solo mensaje, el nonce aleatorio no se reutiliza nunca con la misma clave.
- **Clave fuera del contenedor:** la clave del documento no viaja en el archivo, la URL, el HTML ni el JavaScript. Se guarda en SQLite envuelta con AES-256-GCM bajo la clave maestra, con el ID del documento como AAD.
- **Vínculo con el registro:** el servidor no confía sólo en el ID declarado. El SHA-256 del contenedor completo debe coincidir con el registrado al exportar, y después la etiqueta GCM debe verificarse. Un contenedor truncado, con datos sobrantes, de versión desconocida, con cabecera no canónica o con metadatos sustituidos se rechaza sin descifrar nada.
- **Telemetría no verificada:** un ID inventado o un contenedor que no coincide se registra aparte, sin avisos y sin atribuir el incidente al documento. Un fallo de autenticación indica que la comprobación falló; no prueba un ataque ni un cifrado roto.

## Visor y formatos

El visor muestra texto UTF-8 (`.txt`, `.md`, `.csv`, `.log`, `.json` o sin extensión) e imágenes raster PNG, JPEG, GIF y WebP. El tipo se detecta por contenido y extensión, nunca por lo que declare el cliente.

HTML, SVG, XML, scripts, ejecutables y documentos con macros se marcan como activos. Su contenido nunca se entrega ni se ejecuta, y el resto de formatos se declara «no soportado». El texto se inserta con `textContent`. La CSP (`default-src 'none'; script-src 'self'`…) impide scripts en línea y recursos externos.

Estados del visor: autorización requerida, acceso permitido, acceso denegado, documento extraviado, documento revocado, archivo inválido, formato no soportado, demasiados intentos y servicio no disponible.

## Permisos, sesiones y revocación

- **Cuentas:** se crean de forma explícita con `create-user`; las contraseñas se guardan con scrypt. Un usuario inexistente y una contraseña incorrecta reciben la misma respuesta.
- **Relación con el documento:** quien exportó es la propietaria; un lector necesita un permiso activo. Conocer el ID o tener el archivo no basta. Un tercero recibe 404 en el documento, sus permisos, el contenedor, los eventos y el registro.
- **Comprobación en cada solicitud:** cada endpoint sensible y cada solicitud de contenido vuelve a comprobar la sesión y el permiso.
- **Sesiones y CSRF:** la cookie es `HttpOnly` y `SameSite=Strict`, con un token CSRF por sesión en `X-CSRF-Token`. Se comprueban `Origin` y `Host`, y hay límite de intentos de inicio de sesión, persistido en la base.
- **Auditoría obligatoria:** la decisión de acceso y su evento de auditoría se escriben en la misma transacción `BEGIN IMMEDIATE`. El contenido sólo se devuelve después del `COMMIT`. Si el evento no se puede persistir, la respuesta es 503 y no se entrega nada.
- **Momento efectivo de la revocación:** el `COMMIT` de la transacción que cambia el estado; el panel muestra ese instante como «Efectivo desde». SQLite serializa las escrituras, así que toda solicitud cuya transacción se confirme después ve el estado nuevo.
- **Lo que la revocación no alcanza:** las solicitudes confirmadas antes de ese instante quedaron autorizadas, y una respuesta ya en camino o un contenido ya entregado no se puede retirar.
- **Prueba de concurrencia:** ninguna entrega lleva un número de evento posterior al de la revocación.
- **Durabilidad:** WAL con `synchronous = FULL`. La demo termina el proceso de forma abrupta y comprueba que todo persiste.

## Eventos, avisos y correo

Cada evento registra:

- la hora UTC del servidor;
- el tipo: exportación, cambio de permisos, revocación o extravío, solicitud de acceso, acceso denegado, contenido entregado, contenedor inválido o fallo de integridad;
- el documento validado o el ID sólo declarado;
- la cuenta, o «sin sesión»;
- el resultado y el motivo;
- la IP de la conexión y su origen, la cabecera de proxy recibida, la ubicación aproximada y la ubicación declarada por el navegador.

Los nombres, el agente de usuario y los demás textos se guardan sin caracteres de control ni de dirección bidireccional.

Los avisos iguales (mismo documento, motivo y cuenta) se agrupan durante 15 minutos con su recuento. La cola de correo es persistente:

- **Estados de la cola:** pendiente, enviado y fallido, con reintentos limitados (5 por defecto, con espera exponencial). «Enviado» sólo se marca cuando el servidor SMTP aceptó el mensaje.
- **Estados del aviso:** «desactivado», «sin destinatario» u «omitido por ráfaga» se muestran tal cual.
- **Entrega:** un fallo de correo no pierde el evento ni concede acceso. La entrega es «al menos una vez», así que una caída en mitad de un envío puede duplicar un correo.

El correo no incluye contenido, claves, IP ni coordenadas: remite al panel autenticado. Ejemplo real de la demo:

> Se intentó acceder a Contrato.cerbero, marcado como extraviado. Acceso denegado. Origen: la cuenta «tercero». Ubicación aproximada por IP: no disponible. Ubicación declarada por el navegador: no.

La ubicación del navegador sólo se pide tras pulsar «Compartir mi ubicación» y leer el aviso. Se guarda con su procedencia, el momento informado, el momento de recepción y la precisión declarada. Denegar el permiso se registra, pero no cambia los permisos de lectura.

## Modelo de amenazas (resumen)

| Amenaza | Qué hace el prototipo | Qué no hace |
|---|---|---|
| Copia del `.cerbero` en manos de un tercero | Sin cuenta autorizada no hay contenido; cada intento se registra y, si el documento está extraviado o revocado, avisa | No sabe dónde está el archivo ni detecta ataques fuera de línea |
| Lector con permiso que filtra lo que ve | Auditoría de cada entrega; revocación inmediata para lo que venga después | No impide capturas ni copias; no retira lo ya entregado |
| Contenedor alterado, truncado o con metadatos de otro documento | Rechazo por formato, SHA-256 registrado y etiqueta GCM | — |
| Conocer el ID de otro documento | 404 en toda la API ajena; telemetría sin atribución | — |
| CSRF, *clickjacking*, XSS, DNS rebinding | Token CSRF, `SameSite=Strict`, `Origin`, `TrustedHost`, CSP, `frame-ancestors 'none'`, sólo `textContent` | Fuera de loopback hace falta HTTPS y revisión |
| Fuerza bruta e inundación | Límites de inicio de sesión, aperturas, tamaño y avisos. Cada intento reserva su hueco dentro de una transacción, así que la concurrencia no los elude. Los cuerpos JSON grandes o sin longitud se rechazan antes de autenticar | No es protección DoS de red. El bloqueo por cuenta permite que un tercero impida temporalmente el inicio de sesión de otra cuenta; la orden local `set-state` permite revocar igualmente |
| Cookie plantada desde otro puerto de `127.0.0.1` (las cookies no se aíslan por puerto) | El inicio de sesión siempre crea una sesión nueva y el panel muestra la cuenta activa | Sin HTTPS no se puede usar el prefijo `__Host-`; riesgo residual documentado |
| Cambio de una carpeta por un enlace durante una exportación por ruta | Se resuelve la ruta, se comprueba que está dentro del área y, tras abrir, se compara el archivo abierto con el resuelto | No hay atomicidad: quien puede escribir en el área autorizada aún tiene una ventana mínima |
| `X-Forwarded-For` falsificado | Se ignora sin proxy confiable | — |
| Robo de la base de datos sin la clave maestra | Las claves de documento están envueltas | Con la clave maestra y la base, todo es descifrable |
| Compromiso completo del servidor | Nada | Fuera del alcance |

## Conservación y recuperación de claves

- **Qué guardar:** sólo hay que guardar dos cosas, y por separado:
  - la clave maestra (`master_key_file`, 32 bytes en base64 con prefijo `cerbero-pf-master-v1:`);
  - el directorio de datos (`cerbero_pf.sqlite3` con sus archivos `-wal`/`-shm`, y `containers\`).
- **Las dos piezas hacen falta:** sin la clave, las claves envueltas de la base no sirven. Sin la base, la clave no sirve.
- **Copia de seguridad:** detén el servicio antes de copiar la base (o usa la API de *backup* de SQLite). Guarda la clave fuera del volumen de datos y fuera de las copias de la base, con permisos restringidos. En Windows, por ejemplo: `icacls <archivo> /inheritance:r /grant:r "${env:USERNAME}:(R)"`.
- **Clave ausente o incorrecta:** el servicio se niega a arrancar con un error explícito. Muestra el identificador de la clave esperada y el de la recibida, y no genera otra. Restaura la clave correcta y vuelve a arrancar: no se pierde nada. Lo prueban `test_crypto_and_keys.py` y el arranque manual.
- **`genkey`:** nunca sobrescribe una clave existente.
- **Sin rotación ni depósito:** no hay rotación de la clave maestra ni depósito de claves. Perder el servicio, su base o su clave puede hacer irrecuperables estas exportaciones; el original sigue donde estaba, porque el prototipo nunca lo modifica.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Resultado del 12 de noviembre de 2026: 75 pruebas, 74 correctas y 1 omitida. La omitida es el enlace simbólico de archivo, porque este Windows exige privilegios para crearlo (`WinError 1314`). La contención frente a enlaces sí se prueba con una *junction* de directorio, que no requiere privilegios. El registro completo está en `dev\review\logs\after-2026-11-12-protected-files-tests.txt`.

| Archivo | Cubre |
|---|---|
| `test_crypto_and_keys.py` | Ida y vuelta exacta, clave y nonce por exportación, ausencia de clave en el contenedor, alteraciones (contenido, etiqueta, identidad, cabecera), formato estricto, envoltura ligada al documento, clave maestra ausente, incorrecta o corrupta sin pérdida ni acceso, ubicación de la clave |
| `test_access.py` | Original intacto, bytes exactos (texto e imagen), exportaciones independientes, ninguna clave en las respuestas, contenedores sustituidos, terceros con el ID (API directa), lector sin gestión, CSRF y `Origin`, revocación de permisos, revocación con sesión anterior, copias y reinicio, concurrencia, auditoría que falla, sesiones, bloqueo de inicio de sesión persistente, límite de aperturas |
| `test_location_and_alerts.py` | IP privadas y de loopback, proxy falsificado y de confianza, sin proveedor, base local, proveedor SIMULADO, ubicación del navegador declarada, denegada o inválida, SMTP real a buzón local, fallo como pendiente y después fallido, cola tras reinicio, duplicados y ráfagas, ID inventado sin incidente, SMTP externo sólo con permiso explícito |
| `test_inputs.py` | Nombres maliciosos confinados, texto de registros saneado, frontend sin HTML inyectado, cargas excesivas con y sin longitud, archivos inválidos, formatos activos nunca entregados, rutas y *junctions* fuera del área, cabeceras, host desconocido, *traversal* estático, configuración de ejemplo, ningún secreto en el repositorio |
| `ReviewRegressions` (en tres archivos) | Hallazgos de la revisión adversarial: bloqueo y límite de aperturas con 30 y 20 hilos simultáneos, `set-state` local con la cuenta bloqueada, identificadores con salto de línea, cuerpos JSON grandes o sin longitud, `Origin` detrás de un proxy, números desbordados en la ubicación, `QUIT` fallido tras un `DATA` aceptado |
| `test_e2e.py` | La demo completa contra el servidor real en otro proceso, y el visor y el panel en Chromium con contextos separados: exportación con descarga, autorización requerida, acceso permitido, evento en el panel, marcado como extraviado, copia denegada, sesión anterior denegada, archivo inválido, ubicación denegada y concedida (coordenadas de prueba), aviso, servicio no disponible, sin errores de consola ni violaciones de CSP |

## Registro exportable para revisión

En el panel, «Exportar registro» descarga `cerbero-pf-audit-<id>.json` (formato `cerbero-pf-audit-1`) con el documento, sus eventos, avisos y límites. Sirve para revisar a mano un incidente junto a un caso de Cerbero. La Skill no lo lee ni lo consume automáticamente, y no existe ningún comando UGOS para este servicio.

## Pendiente

- Validar en un NAS UGREEN: despliegue, HTTPS, almacenamiento, permisos de archivos y procesos, y si UGOS permite este servicio.
- Rotación de la clave maestra, copia de seguridad en caliente y depósito opcional de claves.
- Formatos adicionales en el visor (por ejemplo, PDF) con un renderizado seguro.
- Integración real con la Skill. Exigiría capacidades del catálogo que hoy no existen.
