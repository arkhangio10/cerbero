# Prompt para Claude: archivos protegidos de Cerbero

Trabaja en este repositorio e implementa un prototipo funcional de **Cerbero: exportación cifrada, acceso controlado, alertas y revocación**. Entrega código ejecutable, interfaz, pruebas y una demo reproducible. Completa la implementación; no te quedes en una propuesta o pantallas con datos fijos.

## 1. Contexto y alcance

Lee primero `README.md`, `CERBERO_BLUEPRINT.md`, `CERBERO_TECHNICAL_DESIGN.md`, `submission/DECLARATION.md` y las instrucciones locales aplicables. Inspecciona la arquitectura y las pruebas antes de editar. El README describe la skill 1.2.0 y 147 pruebas: comprueba el estado real, no asumas que esos números siguen vigentes.

Cerbero actualmente es una skill de orquestación para UGOS, con laboratorio Python. Esta ampliación autoriza construir un servicio complementario local para desarrollo; la integración y ejecución en un NAS real quedan pendientes de validación. La exclusión de servicios nuevos del prompt anterior correspondía a aquella iteración, no impide este prototipo.

Implementa en `dev/protected_files/` o una ubicación equivalente justificada. Mantén el ZIP de la skill limitado al Markdown permitido y conserva los paquetes existentes. No inventes comandos UGOS para llamar al servicio ni cambies las reglas de recuperación y aprobación de la skill. Para esta iteración, la integración es documental y mediante registros exportables para revisión; no afirmes que la skill ya consume el servicio automáticamente.

## 2. Comportamiento que debe funcionar

El propietario selecciona explícitamente un archivo y obtiene una copia cifrada `.cerbero`. El original permanece intacto. Esto protege las exportaciones realizadas por este flujo; no intercepta cualquier copia o salida de archivos del NAS.

Quien recibe el contenedor lo abre mediante nuestro visor web, cargándolo de forma explícita. El visor muestra que el acceso se registra y solicita autenticación. El servicio comprueba identidad, permisos, integridad y estado del documento antes de entregar contenido legible.

El propietario puede marcar el documento como extraviado o revocar su acceso. Después de confirmar y persistir esa operación, las solicitudes nuevas de contenido se deniegan, incluidas las de sesiones previamente autenticadas y las de copias del mismo contenedor. Documenta el límite de solicitudes autorizadas antes de la revocación y contenido ya entregado.

Un intento sospechoso genera un evento persistente y una notificación visible para el propietario. Una apertura autorizada también queda auditada. No equipares automáticamente un intento con una lectura efectiva ni con un robo.

**Límite fundamental:** no se detecta que alguien rompe el cifrado fuera del servicio. Un archivo pasivo no transmite su ubicación por sí solo. Sin conexión al servicio no hay nueva autorización ni alerta inmediata. No uses macros, ejecutables ocultos, balizas encubiertas ni permisos de ubicación eludidos.

## 3. Arquitectura y cifrado

Prioriza un backend Python pequeño, SQLite persistente y una interfaz sencilla servida por el mismo backend. Puedes usar FastAPI y `cryptography`, con versiones estables compatibles verificadas y dependencias aisladas. Evita añadir infraestructura innecesaria.

Usa cifrado autenticado estándar, por ejemplo AES-256-GCM mediante `cryptography`, con una clave aleatoria independiente por exportación, nonce adecuado que nunca se reutilice con la misma clave y metadatos críticos autenticados. Define un contenedor versionado con identificador opaco, límites de tamaño y formato estricto. No implementes primitivas criptográficas propias. Consulta la [documentación oficial de AEAD](https://cryptography.io/en/latest/hazmat/primitives/aead/).

La clave del documento no viaja en el archivo, URL, HTML ni JavaScript. Guárdala cifrada en el servidor mediante una clave maestra proporcionada por configuración segura, separada de la base de datos y del directorio público. No incluyas secretos reales en el repositorio, fixtures, trazas o ejemplos. Si falta o cambia incorrectamente la clave maestra, falla de forma explícita; no generes otra silenciosamente y vuelvas irrecuperables los documentos existentes.

El descifrado ocurre en el servidor después de autorizar. Para acotar el MVP, permite exportar archivos pequeños con un límite documentado y ofrece visualización segura de texto UTF-8 e imágenes raster seleccionadas. Otros formatos pueden declararse no soportados en el visor. No ejecutes HTML, SVG, scripts o macros cargados. No guardes copias legibles temporales innecesarias.

Vincula el contenedor recibido con el documento registrado mediante evidencia íntegra, no únicamente un ID controlado por el cliente. Rechaza archivos truncados, alterados, versiones desconocidas y metadatos sustituidos. Un fallo de autenticación criptográfica indica que la comprobación falló; no prueba por sí solo un ataque ni un cifrado roto.

## 4. Permisos, persistencia y revocación

Implementa autenticación real, con cuentas de demo creadas explícitamente y credenciales aleatorias o configuradas localmente. Separa propietario, lector autorizado y tercero sin permiso. Conocer el ID o poseer el archivo no debe permitir acceder al contenido, modificar permisos, consultar eventos ajenos ni revocar documentos de otra cuenta.

Comprueba autorización en cada endpoint sensible y cada solicitud nueva de contenido. No basta con ocultar botones o validar solo al iniciar sesión. Usa sesiones seguras, protección contra CSRF cuando corresponda y respuestas de contenido sin almacenamiento en caché. Explica que estas medidas no impiden capturas ni copias del contenido ya visto.

Persiste documentos, permisos, revocaciones, eventos y notificaciones. Define con transacciones el momento en que una revocación queda efectiva. No concedas acceso si fallan las comprobaciones o la persistencia de auditoría requerida. Prueba reinicios y concurrencia relevante. Incluye límites de carga y de intentos, validación de rutas y protección frente a contenido malicioso en nombres y registros.

Por defecto escucha solo en loopback. Documenta que un despliegue fuera del equipo requiere HTTPS y configuración de seguridad revisada. No abras puertos públicos, despliegues servicios remotos ni uses documentos personales para la demo.

## 5. Ubicación y alertas honestas

Registra hora UTC del servidor, documento validado cuando sea posible, identidad autenticada o anónima, resultado y motivo. Distingue al menos solicitud de acceso, acceso denegado, contenido servido, contenedor inválido y revocación. No afirmes que el servidor puede demostrar que una persona leyó el contenido.

Obtén la IP de la conexión. No confíes en `X-Forwarded-For` salvo configuración explícita de proxies confiables. La geolocalización por IP es aproximada y puede reflejar una VPN. Permite una base local opcional; si no existe, la IP es privada/loopback o no hay resultado, muestra «ubicación no disponible». No envíes IP ni documentos a proveedores externos por defecto. Fundamenta los límites con la [documentación de MaxMind](https://support.maxmind.com/knowledge-base/articles/maxmind-geolocation-accuracy).

La ubicación del navegador será opcional y solo se solicitará tras una acción explícita y un aviso claro. Registra procedencia, momento y precisión reportada cuando estén disponibles. Es información declarada por el cliente y puede manipularse; no la uses como prueba de identidad. Denegar el permiso no impide registrar el intento ni cambia por sí solo los permisos de lectura. Sigue la [especificación de geolocalización](https://www.w3.org/TR/geolocation/).

Implementa notificaciones reales y persistentes en el panel, además de un adaptador SMTP configurable. Valida el envío SMTP con un buzón local de pruebas; deja los envíos externos desactivados hasta configurar destinatario y servicio. Usa una cola persistente con reintentos limitados y estados pendiente, enviado o fallido; una falla del correo no pierde el evento ni concede acceso. No declares envío exitoso si solo se encoló. Limita duplicados y ráfagas, conservando su recuento. No adjuntes contenido, claves o coordenadas precisas al correo: remite al panel autenticado.

Ejemplo de mensaje, rellenado solo con evidencia disponible: «Se intentó acceder a Contrato.cerbero, marcado como extraviado. Acceso denegado. Ubicación aproximada por IP: no disponible». Un ID inventado no debe crear un incidente atribuido como probado a otro documento. Separa telemetría no verificada de eventos vinculados al contenedor validado.

## 6. Interfaz y demo

Incluye una interfaz en español con exportación, lista de documentos, permisos, estados, acción de marcar como extraviado/revocar y panel de actividad y notificaciones. El visor debe mostrar estados útiles: autorización requerida, acceso permitido, denegado, revocado, archivo inválido y servicio no disponible.

Prepara un comando o guion breve que cree únicamente datos sintéticos y permita demostrar:

1. Exportar un documento a `.cerbero` y conservar intacto el original.
2. Abrirlo como lector autorizado y ver el evento real.
3. Marcarlo como extraviado desde la cuenta propietaria.
4. Intentar abrir una copia desde otra sesión y obtener denegación, evento y notificación.
5. Ver el mensaje en el buzón SMTP local y su estado de entrega real.
6. Reiniciar el servicio y comprobar que la revocación y los eventos permanecen.

La demo en localhost mostrará ubicación no disponible. Puedes añadir un caso separado con proveedor geográfico simulado para enseñar el aspecto de la alerta, siempre marcado «SIMULADO». No presentes una ciudad inventada como resultado real.

## 7. Pruebas de aceptación

Añade pruebas de comportamiento, incluyendo:

- El original no cambia; dos exportaciones independientes usan claves e identificadores distintos; la recuperación autorizada produce exactamente los bytes originales.
- El contenedor y las respuestas accesibles al lector no contienen la clave; alterar contenido, cabecera autenticada o identidad del documento se rechaza sin liberar texto legible.
- Un tercero no puede leer, revocar, modificar permisos ni ver eventos ajenos, aunque conozca el ID; prueba llamadas directas a la API.
- La revocación persistida bloquea solicitudes posteriores y copias del contenedor, también después del reinicio y con una sesión anterior.
- La falta de conexión no permite una nueva apertura; una clave maestra ausente/incorrecta no provoca pérdida silenciosa ni acceso concedido.
- Las IP privadas, cabeceras de proxy falsificadas, ausencia de proveedor geográfico y negativa al permiso de ubicación tienen resultados correctos y no inventan coordenadas.
- Eventos, cola y reintentos sobreviven a reinicios; un fallo SMTP se muestra como fallo o pendiente, no como éxito; limita duplicados.
- Nombres maliciosos, cargas excesivas, archivos inválidos y formatos activos no ejecutan contenido ni acceden a rutas fuera del área autorizada.
- Un flujo completo usa el servidor real, persistencia real y dos sesiones separadas; verifica también el visor y el panel en navegador si tienes herramientas disponibles.

Ejecuta la suite existente y las dos reproducciones para comprobar que el núcleo sigue funcionando. Desde `dev/`: `python -m unittest discover -s tests`, `python review/reproduce_review.py` y `python review/reproduce_review_2026_11_12.py`. Ejecuta también las pruebas nuevas y el comprobador oficial cuando esté disponible. No debilites pruebas previas ni confundas comprobaciones omitidas con aprobadas. Conserva evidencia de resultados y explica fallos preexistentes o limitaciones del entorno.

## 8. Entrega y cierre

Entrega instrucciones exactas para instalar, configurar, iniciar, probar y ejecutar la demo en Windows/PowerShell. Incluye configuración de ejemplo sin secretos, modelo de amenazas breve, formato del contenedor y procedimiento de conservación/recuperación de claves. Aclara que perder el servicio y sus claves puede impedir recuperar estas exportaciones.

Actualiza README, diseño técnico y declaración de componentes/servicios para distinguir la skill existente del nuevo prototipo. Añade documentación de la demo sin alterar la propuesta oficial o sus métricas como si ya hubiese validación NAS. No presentes cifrado en reposo, registros locales o pruebas de laboratorio como protección frente al compromiso completo del servidor.

Finaliza con archivos modificados, comandos usados, resultados de pruebas, pasos de demo y pendientes reales. Expón claramente: no hay rastreo garantizado fuera del visor, no se detecta descifrado offline, la ubicación no demuestra identidad, revocar no borra contenido ya entregado y la integración UGOS sigue pendiente. Resuelve autónomamente las decisiones reversibles de implementación y continúa hasta completar el prototipo verificable.
