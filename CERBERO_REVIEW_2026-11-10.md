# Revisión independiente de Cerbero 1.0.0

Fecha: 10 de noviembre de 2026. Revisor: Codex, a petición del usuario. Esta revisión añade un informe y un reproductor; no corrige la implementación.

## Resultado

La entrega contiene una Skill conforme al comprobador estático y un laboratorio útil de procedimientos deterministas. Aún hay errores de autorización, alcance, serialización y evaluación que deben corregirse antes de presentar sus métricas como evidencia sólida de calidad.

Los fallos reproducidos pertenecen al laboratorio Python. Las instrucciones de la Skill también tienen vacíos o contradicciones relacionados. Ninguna reproducción se ejecutó en UGOS ni accedió a archivos personales: todas las mutaciones ocurrieron dentro de SimNAS en memoria.

## Verificaciones realizadas

- `python -m unittest discover -s tests -v`, desde `dev/`: **58/58 pruebas pasan**.
- Entre ellas: comprobador oficial **static-pass**, cero errores y cero advertencias; capacidades declaradas; ZIP igual a la carpeta de Skill.
- ZIP existente: `dist/cerbero-guardian-1.0.0.zip`, **30 897 bytes**.
- Propuesta: **492 palabras sustantivas**, PDF de **15 165 bytes**, dos páginas. Se extrajeron y renderizaron ambas páginas; no se observan recortes ni solapamientos. La segunda página tiene mucho espacio libre, cuestión editorial secundaria.
- Se inspeccionaron SKILL.md, las referencias de recuperación/memoria/mapa/aprendizaje/confianza, laboratorio, pruebas, evaluador, generador de datos, guion y declaraciones.
- Se añadieron siete reproducciones independientes. Ejecución: `python dev/review/reproduce_review.py` desde la raíz. En la versión revisada: **0 PASS, 7 FAIL**. Su código de salida 1 significa que se reprodujeron los defectos.

## P0: aprobaciones y alcance

### R01 — Se recupera sin poder guardar el plan obligatorio

Ubicación: `dev/cerbero_lab/variants.py`, `persist()` (427–435) y `recover()` (772–785). Relacionado: `skill/cerbero-guardian/SKILL.md`, persistencia (234–236).

Reproducción: cargar S03 y hacer que SimNAS rechace todas las operaciones `save_text`. El resultado sigue siendo `overall=verified`, se crea una carpeta y se realiza una copia, con `persisted=[]`. No existe un plan persistido cuyo hash pueda haber confirmado el usuario.

Causa: si `plan_file` es None, `plan_digest` también lo es, y la comprobación del plan queda saltada por `if plan_file`. La instrucción general de la Skill dice continuar si un guardado se rechaza, sin separar un informe opcional de un plan obligatorio.

Corrección esperada: una recuperación depende de un plan persistido, verificado, con digest y aprobación exacta. Su fallo/rechazo debe bloquear mkdir/copy; fallar al guardar un informe puede tener otro tratamiento, explícito. Probar también respuesta incompleta y guardado no verificado.

### R02 — Recuperación sin referencia ignora rechazo del plan

Ubicación: `dev/cerbero_lab/variants.py`, `recover_files()` (152–172), llamado desde VariantC (860–862).

Reproducción: S13 con `answers.approve_plan=False` hace una copia, devuelve `overall=verified` y `plan=None`.

Corrección esperada: el modo sin referencia debe compartir el protocolo de plan/aprobación/recibo. Su comprobación sólo puede certificar fidelidad a la fuente elegida. Distinguir ese resultado de la identidad de una versión previamente aprobada.

### R03/R04 — Rutas manipuladas en memoria salen del alcance

Ubicación: `dev/cerbero_lab/variants.py`, `select_source()` (649–669), composición de destino (757), `ensure_dirs()` (139–149). La tabla de slots y delegaciones de SKILL.md acepta rutas de registros cargados, sin definir una validación completa de pertenencia canónica antes del acceso.

R03: cambiar el campo `rel` de A-layout a `../../outside/escaped-layout.indd` en la memoria de S03. Resultado: copia exitosa en `outside/escaped-layout.indd`, fuera de la carpeta y del padre de recuperación previstos, con estado `verified`.

R04: mantener `location=L-bk-old` en una copia, pero cambiar su ruta a `private/other-client/layout.indd`, donde el simulador tiene los mismos bytes. Resultado: Cerbero lee el hash de esa ruta y la copia, aunque no está bajo las ubicaciones autorizadas.

Corrección esperada: comprobar pertenencia por ruta canónica y límites de componentes, no por etiqueta, prefijo textual o memoria previa. Validar fuentes antes de leerlas y destinos antes de crear directorios. Rechazar traversal, rutas absolutas inesperadas y discrepancias entre ruta y ubicación; si no se puede verificar el efecto de un alias/enlace, informar incertidumbre y bloquear la operación dependiente. Aplicar la regla al laboratorio y a las instrucciones de la Skill.

## P1: integridad de memoria y veredictos

### R05 — La serialización cambia rutas

Ubicación: `dev/cerbero_lab/records.py:21`; la prueba `test_round_trip_strips_quotes_and_joins_lists` exige el comportamiento defectuoso.

Reproducción: `/nas/Cliente O'Neil/foto, final.tif` se convierte en `/nas/Cliente ONeil/foto, final.tif` tras Bundle → render → parse.

Causa: `replace("'", "")` elimina datos. También se aplastan saltos de línea y las listas se separan por comas sin escape. El formato no puede representar inequívocamente todos los valores que declara preservar.

Corrección esperada: un contrato de serialización reversible, con escape y tipos definidos, coherente entre Skill, parser, writer y grader. Probar Unicode, apóstrofes, comas, barras, delimitadores y texto multilínea. Rechazar campos duplicados/estructuras inválidas con errores explícitos. No convertir un cambio de dato en una estrategia de escape.

### R06 — El mapa declara recuperables copias no elegibles

Ubicación: `dev/cerbero_lab/mapping.py:46–68`.

Reproducción: en S03, asignar a todas las copias `sha256="0"*64` y `access="denied"`, manteniendo sus IDs de versión y estado current. La consulta sobre pérdida de la carpeta devuelve `recoverable`, con copias elegibles para todos los miembros.

Causa: `evaluate_member()` no contrasta el hash de la copia con el hash de la versión y no valida acceso/procedencia. Confía en el enlace `version`. La memoria de fixtures ni siquiera representa todos los campos exigidos por la Skill.

Corrección esperada: una sola definición de elegibilidad compartida y probada, con estados explícitos para acceso, frescura, versión, procedencia, dominios y cobertura. Diferenciar una copia inválida de un dato desconocido; una observación antigua no equivale a acceso comprobado ahora. Añadir topologías contradictorias y ciclos a las pruebas del mapa.

### Persistencia entre sesiones y grader: contratos incompatibles

Observaciones por inspección, adicionales a los siete probes:

- VariantC usa `CAS-0001` y contadores desde cero en cada instancia (`variants.py:372–384`). `finish()` escribe siempre `IDX-0001` (870–874). El laboratorio recibe `Memory` construido directamente de fixtures, por lo que no verifica una segunda sesión reconstruida exclusivamente desde los bundles guardados.
- El formato documentado de `receipt-entry` no exige `asset_id` (`references/memory-records.md:91`), pero el grader accede a él obligatoriamente (`grader.py:57`).
- El grader relaciona recibos mediante convenciones de nombres y compara IDs como `A-layout` y rutas relativas del fixture. La Skill genera IDs AST y el NAS tendrá un prefijo real distinto. La instrucción del guion de exportar y calificar directamente necesita un mapa de correspondencias o identidades estables.
- El grader comprueba afirmaciones de los recibos, no los bytes de destino. Esto ya se admite en su documentación, pero debe conservarse esa distinción en la evidencia final.

Corrección esperada: probar Baseline → exportación → nueva sesión → carga de memoria → incidente → recuperación → otra sesión, sin inyectar el objeto Memory original. IDs únicos, índices completos, resolución de supersedes y trazabilidad explícita entre recibos y entradas. Probar el grader con una traza construida según la documentación, no sólo emitida por VariantC.

## P1: la evaluación actual necesita repetirse

### R07 — Las variantes comparten memoria mutable

Ubicación: `dev/tools/run_evaluation.py:38–46`; `dev/cerbero_lab/variants.py:880–897`.

Reproducción S14: ejecutar C y después C-no-selector sobre el mismo Scenario da **37 llamadas** y ninguna conclusión revalidada para la segunda variante. Ejecutar C-no-selector con el fixture fresco da **38 llamadas** y revalida CLM-0000-0001 y CLM-0000-0002.

Causa: `memory = scenario.memory` comparte el objeto que C modifica al detectar contradicciones. Las cifras dependen del orden de evaluación.

Corrección esperada: aislar estado por ejecución/variante; probar invariancia al orden y repetir todas las métricas. Mantener los denominadores comparables: C-no-selector actualmente omite S13, de modo que los totales no abarcan los mismos casos.

### Falta ejecución del modelo sobre la Skill real

Las 58 pruebas ejecutan Python determinista y comprobaciones estáticas. Son útiles, pero no prueban que un modelo leyendo SKILL.md produzca esas delegaciones, conserve los datos o respete las pausas.

Siguiente nivel: un harness de desarrollo que cargue la Skill real y permita a un agente usar expertos simulados mediante respuestas controladas. Registrar decisiones, delegaciones, estados de espera, aprobaciones y efectos. Incluir respuestas de experto incompletas, errores desconocidos, waiting_user/waiting_approval y casos adversariales. No presentar esta prueba como validación de UGOS.

El `memory-seed` coloca casos de desarrollo y holdout, con respuestas esperadas, en un único bundle (`make_demo_dataset.py:81`). La lectura completa de ese bundle permite al modelo verlos antes de congelar una regla. Para medir generalización de un agente, el runner debe reservar las entradas/etiquetas y revelar cada partición en el momento correspondiente; el diseño actual sirve como replay de casos, no demuestra un holdout ciego.

## P2: entrega y demo

1. **Declaración de IA incompleta.** `submission/DECLARATION.md:60` dice "No other AI tool was used" y sólo lista Claude. En esta conversación Codex hizo la investigación, los documentos de producto/arquitectura y esta revisión. Incluir ese uso en declaración, disclosures y propuesta. No adivinar versiones de modelos no verificadas.
2. **Privacidad no validada.** La propuesta y declaraciones aseguran que contenido, rutas y hashes permanecen en el NAS. Usar sólo expertos registrados no demuestra dónde se ejecutan todos los modelos. Expresar lo comprobado: la Skill no integra servicios externos propios; localización del procesamiento y flujos del runtime deben verificarse en la configuración asignada. No afirmar 100% local/offline sin evidencia.
3. **Comparación comercial excesiva.** La propuesta afirma de forma general que los asistentes eligen por nombres/fechas. Lo demostrado es el comportamiento del baseline A implementado. Describir ese baseline con precisión o aportar comparación externa válida.
4. **Datos de demo.** Los archivos llamados PDF/TIF/DOCX/ARW contienen texto repetido. Esto sirve para probar hashes, pero no demuestra apertura de documentos o imágenes recuperadas. Añadir un pequeño subconjunto sintético con formatos válidos para mostrar una recuperación utilizable; mantener el resto etiquetado como fixture binario.
5. **Guion.** "Recorded on..." debe ser instrucción de grabación futura mientras no exista evidencia NAS. Mantener la distinción entre plan, simulación, pruebas de agente y ejecución en dispositivo.
6. **UX de confirmaciones.** El informe actual cuenta 79 solicitudes de aprobación de C frente a 31 de B, con 52 guardados. Evaluar agrupación de checkpoints opcionales y ruido de interfaz sin omitir aprobaciones oficiales ni la vinculación del plan. El número real depende de UGOS y no está validado.

## Próxima iteración recomendada

Corregir P0 y P1, añadir regresiones, hacer compatible la persistencia con el protocolo documentado, repetir la evaluación aislada y ejecutar una primera prueba de agente sobre la Skill real. Después corregir las afirmaciones de entrega y construir una nueva versión, conservando el ZIP 1.0.0.

No hacen falta nuevas funciones para esta iteración. El objetivo es que la lógica que se anuncia resista entradas y estados que no están cubiertos por los fixtures originales.
