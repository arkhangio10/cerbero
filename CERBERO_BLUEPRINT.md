# CERBERO

**Tres cabezas. Una memoria. Anticipación, investigación y recuperación comprobada.**

Diseño de producto v3 para UGREEN Hackathon 2026. Fecha de revisión: 10 de noviembre de 2026. La especificación de arquitectura, registros, algoritmos, estados, evaluación y decisiones de implementación está en [CERBERO_TECHNICAL_DESIGN.md](CERBERO_TECHNICAL_DESIGN.md).

Estado:

- **Skill implementada.** `skill/cerbero-guardian` v1.1.0 pasa el comprobador oficial del kit 0.7.3 sin diagnósticos y está empaquetada en `dist/`, junto con la v1.0.0, que se conserva. La v1.1.0 corrige los defectos R01–R07 de la revisión independiente.
- **Laboratorio local.** Hay un laboratorio con 15 escenarios sintéticos, 5 casos de política y 114 pruebas. Contrasta las reglas de decisión contra expertos simulados y recarga la memoria sólo desde archivos guardados entre sesiones. Un harness aparte deja que un modelo siga el `SKILL.md` real frente a expertos simulados; sigue siendo evaluación local, no UGOS.
- **Sin validación en el NAS.** Las cifras de evaluación son de simulación y no demuestran comportamiento en UGOS. Las escenas de demostración siguen siendo un guion.

## 1. La propuesta

Cerbero es una Skill de resiliencia de datos para UGREEN AI NAS. Mantiene un mapa de versiones, copias y dependencias aprobadas; evalúa qué se perdería ante un fallo supuesto; investiga cambios mediante consultas dirigidas; recupera conjuntos coherentes con comprobaciones explícitas; y somete las nuevas políticas de defensa a casos y contraejemplos antes de activarlas.

Usuario inicial: un estudio creativo pequeño que guarda originales, entregables y documentación de clientes en su NAS, sin un especialista dedicado a recuperación de datos.

Problema: cuando faltan archivos o aparecen versiones alteradas, el usuario necesita saber qué cambió, qué copia conserva el contenido esperado, cómo recuperarlo y qué debe modificar para reducir el riesgo de repetición.

Pitch en inglés:

> Cerbero maps what your NAS can recover, investigates unexpected changes by choosing the next useful check, verifies coherent recovery, and tests lessons from incidents before turning them into protection policies.

Track propuesto: Open Innovation.

Alcance inicial: integridad, preparación para recuperación y recuperación de archivos dentro de ubicaciones autorizadas. Los eventos de cámaras pueden enriquecer futuros casos físicos, pero no son una dependencia de la demostración principal.

## 2. Las tres cabezas

| Función | Trabajo concreto | Resultado visible |
|---|---|---|
| Guardián | Relacionar versiones, copias y dominios de fallo; evaluar la pérdida hipotética de una ubicación | Mapa de recuperabilidad con supuestos y cobertura explícitos |
| Investigador | Elegir la siguiente comprobación que resuelve una duda relevante; registrar soporte y contradicciones | Evidencia enlazada, hipótesis revisadas y preguntas pendientes |
| Rescatista | Recuperar un conjunto coherente ligado a un plan aprobado; verificar destinos y evaluar una lección | Recibo de recuperación y política probada con contraejemplos |

Las cabezas son etapas del producto. La implementación debe delegar el trabajo a los agentes registrados del catálogo, sin asumir que se pueden instalar agentes personalizados.

## 3. Qué significa proteger

En esta versión, proteger significa conocer el estado esperado, comprobar la recuperabilidad y aplicar controles a las operaciones que el usuario solicita a Cerbero.

El disparador inicial es una petición del usuario. No se ha identificado en el catálogo una capacidad para instalar vigilancia permanente, interceptar escrituras de otras aplicaciones, recibir todos los eventos del sistema, cambiar reglas de firewall o detener procesos maliciosos.

Cerbero debe mostrar el momento y el alcance de la última revisión. Una revisión anterior no implica protección continua. Tampoco puede asegurar que un cambio de contenido provenga de un ataque: puede ser una edición legítima, una sincronización, un error o una acción no autorizada.

## 4. La memoria

La persistencia usa archivos de texto Markdown:

- **Dónde:** una carpeta que el usuario autoriza.
- **Cómo se guardan:** con `ug-knowledge save-text`, como paquetes `CERBERO-*` en el formato `cerbero-memory-2` (valores JSON, reversibles).
- **Cómo se leen:** con `ug-filesystem cat`, más índices con digest.
- **Qué no requiere:** desplegar una base vectorial, entrenar un modelo ni incluir scripts en el ZIP de la Skill.

**Memoria de referencia:** archivos críticos, rutas verificadas, tamaño, fecha de observación, hash SHA-256 cuando corresponda, versiones aprobadas, conjuntos de versiones compatibles y fuentes de recuperación. Las copias incluyen el dominio de fallo sólo cuando existe evidencia o una declaración con procedencia; rutas distintas no prueban independencia. Una referencia expresa el contenido esperado en un momento concreto; no demuestra que el archivo esté libre de malware.

**Memoria de incidentes:** identificador del caso, alcance, observaciones, referencias de evidencia, contradicciones, hipótesis, operaciones realizadas, aprobaciones, verificaciones finales y elementos sin resolver. Cada afirmación conserva sus dependencias y se revisa si cambia una fuente. Se distingue lo observado, lo declarado y lo inferido. Dos resúmenes del mismo documento no cuentan como evidencia independiente.

**Memoria de defensa:** reglas propuestas, ámbito, motivo, caso de origen, vigencia, pruebas y resultados. Una regla debe superar el incidente original, un caso similar, un contraejemplo legítimo y un caso con información insuficiente antes de presentarse para aprobación. Se conservan versiones anteriores y las políticas nunca pueden ampliar permisos o suprimir comprobaciones esenciales.

Ejemplo de aprendizaje: tras perder originales en una carpeta que antes no era crítica, el usuario aprueba incorporar esa carpeta a las verificaciones completas y exigir una copia contrastada antes de reorganizaciones solicitadas a Cerbero.

Aprender significa recuperar casos pertinentes y aplicar políticas revisadas. No significa reentrenar el modelo, reescribir sus restricciones ni tratar cada incidente como una prueba de ataque.

La memoria guardada en el mismo NAS no es inmutable. Si un atacante controla el dispositivo y puede modificar archivos, memoria y copias, los hashes guardados allí no constituyen una raíz de confianza independiente. La referencia y las copias importantes necesitan una protección independiente para soportar ese escenario; esa configuración no está automatizada por esta propuesta.

## 5. Motor de investigación eficiente

Flujo: alcance autorizado → mapa de versiones/copias → evaluación de fallos hipotéticos → selección de la siguiente comprobación → hipótesis y contradicciones → contrato de recuperación → aprobación → ejecución → recibo verificado → reproducción de casos → política aprobada.

La evaluación de fallos es una consulta al mapa: excluir las copias afectadas por el escenario y comprobar si todas las versiones de un conjunto aprobado siguen teniendo una fuente elegible. Es una predicción condicionada al inventario y a los dominios conocidos, no una simulación completa del NAS. Un ensayo real de copia y verificación aporta evidencia adicional.

1. Resolver las ubicaciones reales y el alcance solicitado. No inventar rutas de papeleras, respaldos o archivos.
2. Enumerar archivos dentro de límites explícitos. Registrar truncamiento, permisos denegados y elementos no revisados.
3. Usar metadatos para priorizar, conservando una distinción entre revisión de metadatos y verificación de contenido. Fechas o tamaños iguales no garantizan contenido idéntico.
4. Calcular hashes de todos los archivos declarados críticos dentro del alcance de la revisión. Si no termina, informar cobertura parcial.
5. Recuperar del índice de memoria sólo los casos y políticas pertinentes. Reutilizar una extracción anterior únicamente cuando el hash del archivo fuente siga coincidiendo y la extracción sea adecuada para la tarea.
6. Leer con IA los documentos que puedan resolver una pregunta concreta. Priorizar dudas que bloquean la recuperación de activos críticos y, entre alternativas comparables, comprobaciones de sólo lectura que discriminen más hipótesis con menor coste. Los hashes y rutas sustentan comparaciones exactas; la IA interpreta contexto y propone la siguiente consulta. Es una heurística de orquestación, sin probabilidades inventadas ni promesa de optimalidad.
7. Detener búsquedas cuando se alcanza el objetivo, se agota el alcance/budget declarado o faltan capacidades o evidencias. No inventar una respuesta para cerrar el caso.
8. Revalidar la fuente antes de copiar y verificar el destino después. Si los archivos cambian durante el proceso, invalidar el resultado afectado y solicitar un entorno estable.

La eficiencia debe medirse por llamadas reales a herramientas, bytes procesados cuando estén disponibles, tiempo observado, cobertura y precisión. No se promete una mejora de velocidad antes de medirla en el dispositivo.

## 6. Recuperar lo perdido

La vía principal de la demo será un conjunto de copias accesibles y autorizadas cuyos hashes coincidan con el conjunto de versiones aprobado. Así se evita mezclar la última versión de cada archivo cuando pertenecen a entregas incompatibles. Cerbero recuperará hacia una carpeta nueva, después de aprobarse un plan concreto identificado por su contenido y hash.

Cada plan especifica precondiciones, operaciones y postcondiciones. El recibo posterior conserva los resultados reales, los hashes de destino y la cobertura. Cambios en fuente, destino o alcance invalidan la parte afectada del plan; una recuperación parcial no se presenta como éxito global. Estas comprobaciones no constituyen un verificador formal ni garantizan atomicidad del sistema de archivos.

Los archivos alterados se mantienen para comparación cuando sean accesibles y el alcance lo permita. No se sobrescribe silenciosamente una versión actual.

El catálogo también incluye una operación de restauración. Su ejemplo apunta a la papelera, pero quedan por verificar la resolución de la ruta real, permisos, conflictos y semántica del resultado. Esa vía es opcional hasta probarla.

Una copia idéntica a una referencia aprobada demuestra coincidencia de contenido con esa referencia; no prueba por sí sola la erradicación de malware, la identidad de quien hizo cambios ni la seguridad del sistema.

Si el incidente real implica actividad maliciosa todavía activa o integridad dudosa del NAS, la recuperación queda pendiente de que una persona responsable restablezca un entorno confiable. Cerbero no cuenta con capacidades documentadas de aislamiento o erradicación.

No se promete descifrar archivos sin claves, recuperar datos sobrescritos sin una fuente existente o rescatar archivos desde sistemas ajenos.

## 7. Qué significa salir al exterior

La intención de producto es consultar conocimiento público confiable sobre un problema y evaluar su aplicabilidad al caso, manteniendo los archivos privados dentro del alcance autorizado.

**Disponible como base de diseño:** consultar el conocimiento oficial mediante `ug-knowledge answer-official` y leer guías que el usuario haya incorporado a una carpeta autorizada. La respuesta oficial debe conservar las referencias que realmente devuelva; no se presupone que sea una búsqueda web actualizada.

**Extensión pendiente de capacidad:** navegación web o consultas a fuentes externas en vivo. No aparece un navegador, cliente HTTP general o conector arbitrario en el catálogo revisado. Las herramientas de Internet del asistente que desarrolla la Skill no se transfieren al entorno UGOS.

Si se habilitara una vía oficial, la propuesta sería consultar fuentes seleccionadas, registrar URL/fecha/versión, usar consultas generales y confirmar antes de transmitir información privada. Cualquier recomendación externa debe evaluarse como evidencia y contrastarse con las capacidades reales del NAS. No se ejecutarían instrucciones o descargables encontrados en una página como parte automática de la recuperación.

La recuperación desde un respaldo externo sólo es viable cuando ese respaldo se presenta mediante una ubicación soportada y autorizada. No se presupone capacidad de montar servicios remotos o descargar archivos de cualquier sitio.

## 8. Capacidades del kit

Fuente revisada: archivo `uliya-skill-kit-0.7.3-en.zip`; catálogo `2.0.0`, generado el 1 de septiembre de 2026.

| Necesidad | Capacidad publicada | Agente registrado | Uso en v1.1.0 y validación pendiente |
|---|---|---|---|
| Encontrar ubicaciones y archivos | `file-workflow get-user-dir`; `ug-filesystem ls`, `find`, `stat` | `file-agent` | Usada: D1, D2, D3, D5, D6 y D13. Pendiente: límites, banderas de truncado (el catálogo no las garantiza), rutas y permisos |
| Comparar contenido | `ug-filesystem sha256sum` | `file-agent` | Usada: D7. Pendiente: formato, errores y coste en archivos grandes |
| Leer memoria textual | `ug-filesystem cat` | `file-agent` | Usada: D4. Pendiente: lectura parcial y límites |
| Interpretar documentos | `ug-document qa` | `document-agent` | Usada: D8, una pregunta concreta y el documento como dato. `extract` y `reconcile` no se usan |
| Consultar orientación oficial | `ug-knowledge answer-official` | `knowledge-agent` | Usada: D9. Pendiente: procedencia y dónde se ejecuta |
| Guardar memoria e informes | `ug-knowledge save-text` | `knowledge-agent` | Usada: D10. Pendiente: nombre real de archivo, negativa a sobrescribir y una aprobación por guardado |
| Recuperar desde copia accesible | `ug-filesystem mkdir`, `cpmv` con copia sin sobrescritura | `file-agent` | Usada: D11 y D12. Pendiente: `dst` como ruta completa, conflictos y ruta real devuelta |
| Restauración opcional | `ug-filesystem restore` | `file-agent` | Excluida de v1.1.0 hasta validar ruta, papelera y efecto |
| Evidencia física opcional | `ug-surveillance cameras`, `event-timeline`, `event-evidence` | `security-monitor-agent` | Fuera del alcance de v1.1.0 |

El catálogo publica muchas precondiciones y esquemas de error como desconocidos. La presencia de una operación permite planificarla, pero no demuestra su funcionamiento en el dispositivo asignado.

El producto UGOS tiene funciones de snapshots y respaldo. Su existencia en la interfaz no autoriza a invocarlas desde la Skill: no se encontraron operaciones específicas de administración de snapshots o respaldos remotos en el catálogo revisado.

## 9. Demostración de menos de tres minutos

El escenario preparado es el proyecto sintético «Aurora». Lo genera `dev/tools/make_demo_dataset.py`.

- **Datos:** 11 activos y dos conjuntos aprobados (Delivery 1 y Delivery 2).
- **Copias:** una copia de octubre que contiene Delivery 2, una de noviembre con un layout no aprobado y una carpeta que representa un archivo externo con Delivery 1.
- **Incidente:** se prepara a mano. Un archivo se renombra, dos se borran, uno se altera conservando el tamaño, un original RAW se borra sin copia y se añade una nota con instrucciones maliciosas.
- **Dominios de fallo:** se declaran con veracidad para el NAS de pruebas.

Es una simulación controlada de pérdida e integridad, sin ransomware real. El guion definitivo está en [submission/DEMO_SCRIPT.md](submission/DEMO_SCRIPT.md).

| Tiempo orientativo | Lo que verá el jurado |
|---|---|
| 0:00–0:25 | Una consulta hipotética muestra qué versión perdería recuperabilidad si una ubicación deja de estar disponible |
| 0:25–0:55 | Cerbero investiga el incidente preparado; una comprobación de hash distingue un archivo renombrado de uno perdido |
| 0:55–1:25 | Descarta una combinación de copias recientes incompatible con el conjunto aprobado y encuentra fuentes coherentes |
| 1:25–1:55 | Presenta un plan, recibe aprobación, copia a una carpeta nueva y registra comprobaciones de cada destino |
| 1:55–2:30 | Una regla candidata se contrasta con un caso legítimo; el contraejemplo obliga a restringir la regla |
| 2:30–2:55 | El usuario aprueba la política revisada y una segunda consulta muestra su aplicación y la evidencia usada |

La secuencia debe registrarse con la Skill funcionando en el NAS asignado. Los tiempos son un guion, no latencias prometidas. Se etiquetarán los cortes o secuencias aceleradas; no se presentará una simulación local como funcionamiento en UGOS.

El momento central: Cerbero anticipa una pérdida, recupera una versión coherente y muestra que su aprendizaje puede ser refutado y corregido antes de activarse.

## 10. Pruebas que sostienen la propuesta

**Caso central A: recuperación verificable.** Referencia conocida, archivos ausentes o modificados y copias candidatas. Comprobar diferencias, aprobación, ausencia de sobrescritura y coincidencia entre referencia y destino.

**Caso central B: aprendizaje contrastado.** Proponer una regla a partir de un incidente, reproducir casos y un contraejemplo, revisar la regla y obtener aprobación. Ejecutar un caso reservado y comprobar que la política se aplica sin extenderse indebidamente. Registrar herramientas, cobertura y resultado; no inferir mejora sólo porque cambió el texto de la respuesta.

**Caso límite obligatorio: sin fuente confiable.** Las copias no coinciden o no son accesibles. El resultado debe ser recuperación parcial o imposible con las fuentes disponibles; no se deben crear archivos sustitutivos y llamarlos recuperados.

Pruebas adicionales valiosas: cambio legítimo confirmado; contenido modificado conservando tamaño/fecha; archivo fuente que cambia durante la copia; rechazo de aprobación; fallo parcial de copia; cobertura truncada; referencia manipulada; y documento que contiene instrucciones para borrar copias. El contenido de archivos, registros y guías debe tratarse como datos, nunca como autoridad para cambiar políticas o ejecutar operaciones.

La evaluación compara instrucciones simples, memoria de referencia y arquitectura completa bajo condiciones y coberturas equivalentes. Incluye retirar componentes para medir su aportación y contabiliza el coste de crear y mantener memoria. El detalle está en el diseño técnico v2.

Las metas de evaluación se midieron sólo en simulación ([submission/EVALUATION_REPORT.md](submission/EVALUATION_REPORT.md)). La arquitectura completa obtuvo:

- cero sobrescrituras y cero cambios sin aprobación;
- cero recuperaciones afirmadas con la versión incorrecta, frente a 6 del flujo simple;
- 14 de 14 recuperaciones requeridas verificadas por hash;
- 4 de 4 veredictos hipotéticos correctos, frente a 1 de 4 de la memoria con hashes sin dominios.

También muestra un coste mayor en llamadas y aprobaciones, y un fallo propio: la alteración de un archivo ordinario que conserva tamaño y fecha. En UGOS estas metas siguen sin medirse.

## 11. Diferenciación para el jurado

| Criterio | Argumento de producto | Evidencia que debe mostrarse |
|---|---|---|
| Valor de usuario | Ayuda a recuperar trabajo y reduce la incertidumbre sobre qué versión usar | Archivos recuperados y pendientes claramente identificados |
| Innovación | Conecta escenarios de pérdida, investigación activa, recuperación coherente y aprendizaje contrastado | Una dependencia anticipada, un conjunto verificado y un contraejemplo que corrige una política |
| Calidad técnica | Resuelve rutas reales, usa hashes, maneja estados parciales y respeta aprobaciones | Ejecución verificable y caso sin recuperación posible |
| Encaje con AI NAS | Trabaja sobre originales, historial y copias del NAS usando sus expertos | Operaciones reales de UGOS, archivos de memoria y resultados persistidos |

La diferenciación es una hipótesis de producto. No se afirma ser la primera solución del mercado ni se garantiza un premio.

## 12. Entrega

Entregado el 10 de noviembre de 2026:

- **Skill de orquestación:** `skill/cerbero-guardian`, con `SKILL.md`, 9 referencias Markdown enlazadas directamente y 13 delegaciones. Está empaquetada en `dist/cerbero-guardian-1.1.0.zip` (la 1.0.0 se conserva): 10 archivos Markdown, sin scripts, binarios, backend, claves ni datos personales.
- **Laboratorio de desarrollo:** `dev/`, separado del paquete.
- **Propuesta en inglés:** `submission/PROPOSAL.md` y su PDF de 2 páginas. Las diez respuestas suman 492 palabras.
- **Materiales:** guion de demo, declaración de componentes y fuentes, informe de evaluación y lista de validaciones pendientes en el NAS.

Orden seguido:

1. registros con procedencia;
2. mapa y conjuntos aprobados;
3. investigación activa;
4. contratos y recibos;
5. políticas con contraejemplos;
6. comparación de variantes y pruebas de fallos;
7. empaquetado oficial.

Queda pendiente la validación y la grabación en el NAS, sólo para finalistas. La consulta web en vivo y la investigación con cámaras siguen siendo extensiones condicionadas a capacidades verificadas.

## Fuentes

- [Reglas oficiales del hackathon](https://ugreenhackathon.devpost.com/rules).
- [Hackathon Starter Kit](https://ai.ugreen.com/pages/hackathon-starter-kit).
- [Archivo oficial del kit 0.7.3](https://cdn.shopify.com/s/files/1/0630/9416/1602/files/uliya-skill-kit-0.7.3-en.zip?v=1790578898), inspeccionado directamente para el mapeo de operaciones.
- [UGREEN: Files Recycle Bin Features Guide](https://support.ugnas.com/detail/article/en-US/159). Documenta recuperación de elementos aún presentes y límites de acceso; no equivale a un contrato de la CLI del hackathon.
- [UGREEN: Snapshot User Guide](https://support.ugnas.com/detail/article/en-US/654). Documenta una función del producto; no se presume que esté expuesta a la Skill.
- [CISA/MS-ISAC: Ransomware Guide](https://www.cisa.gov/sites/default/files/publications/CISA_MS-ISAC_Ransomware%20Guide_S508C_.pdf). Referencia general para la importancia de copias independientes y probadas; no se incorpora como capacidad automática de Cerbero.
