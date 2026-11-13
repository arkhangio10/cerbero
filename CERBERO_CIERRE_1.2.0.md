# Cerbero 1.2.0: qué falta para cerrar

Revisión independiente: 12 de noviembre de 2026. Se contrastó el resultado comunicado con el repositorio, las pruebas, las trazas, el paquete, el PDF y las reglas oficiales. No se modificó el producto ni se ejecutaron nuevos modelos o pruebas sobre NAS.

## Estado verificado

| Comprobación | Resultado observado |
|---|---|
| Suite | 147/147, ejecutada de nuevo |
| Reproducciones anteriores | 7/7 y 4/4, ejecutadas de nuevo |
| Paquete | 1.2.0 coincide con el Skill, 10 Markdown, 46.024 bytes; comprobado por la suite |
| SHA-256 del ZIP | `db1ce2742fd9e593b6daab105518b21ce9c529ea8e3e3cf8a8742cc1761df733` |
| Checker oficial | pasa dentro de la suite |
| Propuesta | 478 palabras en las diez respuestas |
| PDF | 15.963 bytes, dos páginas inspeccionadas visualmente, texto legible sin cortes |
| Trazas 1.2.0 recalificadas | AG04 12/12; AG05 24/24; AG06 12/12; AG07 11/11; AG08 25/25; AG09 12/12 |
| Skill y referencias de AG04–AG09 | sus hashes coinciden con los archivos actuales |
| Hardware UGOS | pendiente; ninguna de las comprobaciones anteriores demuestra ejecución sobre NAS |

## Última iteración local recomendada: 1.2.1

### 1. Completar una cadena de aprendizaje ejecutada por el agente

El laboratorio ya demuestra persistencia entre procesos. La evidencia de agentes todavía está separada: AG07 rechazó su primera regla y dejó v2 pendiente de nuevos casos reservados; AG09 cargó una regla producida por el procedimiento Python de la demo. Es una respuesta correcta de AG07, pero no demuestra que el agente haya completado todo el ciclo.

Aceptación: un agente produce y evalúa una política, recibe aprobación y guarda su estado; una sesión nueva carga exclusivamente esos archivos, aplica la regla y posteriormente respeta su retiro. El estado que llega a la segunda sesión debe proceder de la primera ejecución del agente. Conservar el rechazo original. Si se revisa una regla después de ver los casos reservados, utilizar otros casos realmente nuevos; no cambiar las respuestas esperadas para obtener un aprobado.

### 2. Cerrar las ambigüedades de las instrucciones

- `Required input` debe variar por modo: copiar archivos elegidos sin referencia no requiere una carpeta de proyecto ni un conjunto aprobado.
- Especificar la conservación de IDs al volver a guardar registros tras un fallo y cómo se resuelven duplicados o revisiones contradictorias.
- Documentar los tipos de `claim` admitidos y su tratamiento cuando aparece uno desconocido.
- Resolver la discrepancia de `contentBytes`: AG04 aceptó un guardado con un byte de diferencia pese a la regla literal. El transporte ya fue corregido; repetir el caso y exigir la regla declarada. Cualquier normalización que se decida permitir necesita definición previa, comprobación del contenido y pruebas específicas antes de aprobar el plan.

Aceptación: instrucciones, procedimiento Python y evaluador tienen la misma semántica; el agente no necesita introducir excepciones improvisadas.

### 3. Reparar los datos de prueba y congelar sus versiones

`agent_memory` convierte rutas de bundles ya guardados y recalcula índices, pero deja referencias a hashes antiguos de planes. AG08 y AG09 detectaron esos desacuerdos. Preparar las rutas definitivas antes de guardar y aprobar los planes, o aplicar una transformación consistente de todas las dependencias desde el estado previo a aprobación. Una fixture de éxito no debe contener corrupción accidental; conservar una fixture separada que sí pruebe corrupción intencionada.

La procedencia de AG04–AG09 confirma que el Skill y sus referencias coinciden con el paquete; los hashes registrados del harness y del evaluador difieren de los archivos actuales. Esto concuerda con modificaciones posteriores documentadas y no invalida por sí solo las trazas. La recalificación actual sigue pasando, pero para cerrar la versión conviene producir ejecuciones nuevas con las herramientas finales y registrar ambas versiones: ejecución y evaluación.

Aceptación: las fixtures válidas empiezan con cadenas íntegramente verificables; los casos adversos conservan su manipulación explícita; cada ejecución identifica Skill, referencias, harness, evaluador y datos efectivos, incluidas las fixtures heredadas. Repetir el flujo principal y las condiciones afectadas en la versión final.

### 4. Afinar la propuesta y la explicación al usuario

La pregunta 9 del PDF presenta el reinicio y retiro normal de una política como caso límite. Es más claro usar como caso adverso una fuente que cambia durante la copia, o una política manipulada tras reiniciar. Mantener recuperación y reconstrucción como los dos casos principales, y conservar la demostración de aprendizaje.

En la pregunta 7, precisar que el plan previo se exige para las operaciones de recuperación; la expresión actual «Every change needs a saved plan» también parece abarcar guardar ese mismo plan. Aclarar «No external service» como ausencia de servicios propios añadidos por Cerbero; la ubicación de procesamiento de UGOS sigue pendiente de validación.

El resumen humano debería empezar por algo como: «5 de 5 archivos de la entrega reconstruidos y verificados; un original fuera de la entrega no tiene copia». El plan mantiene toda su evidencia, pero el usuario debe entender el resultado sin interpretar hashes.

Regenerar el PDF después de los cambios y mantener las diez respuestas por debajo de 500 palabras. Ajustar versión y resultados en todos los documentos. Conservar 1.2.0 y producir un ZIP nuevo idéntico a la versión final.

## Qué permite entregar en primera ronda

Las [reglas oficiales](https://ugreenhackathon.devpost.com/rules), consultadas directamente en esta revisión, exigen PDF con las diez respuestas y ZIP inicial. No exigen acceso al NAS, vídeo ni repositorio público en primera ronda; tampoco exigen que el paquete inicial ya sea plenamente instalable u operativo sobre el dispositivo.

El cierre anunciado es el **15 de noviembre de 2026 a las 23:45 PST**, equivalente al **16 de noviembre a las 02:45 en Lima**. El envío por Devpost y la selección de sus campos no se han realizado en esta revisión. La falta de hardware no debe impedir preparar o enviar la candidatura inicial.

Archivos actuales:

- `submission/cerbero-guardian-proposal.pdf`
- `dist/cerbero-guardian-1.2.0.zip`

Si se completa 1.2.1 antes del envío, usar su PDF y su ZIP coherentes, preservando los anteriores. No presentar el laboratorio como ejecución en UGOS.

## Qué falta para la final, si seleccionan el proyecto

Las reglas prevén un día asignado de acceso al NAS para cada finalista. Priorizar las dependencias que pueden impedir toda la ejecución: instalación, rutas reales, D3 y sus filtros, guardado y fragmentación, lectura completa, destino de copia y aprobaciones. Registrar las respuestas reales y los límites que el dispositivo exponga.

Después ejecutar recuperación, reconstrucción y aprendizaje entre sesiones sobre los datos sintéticos, medir tiempo, operaciones, bytes y confirmaciones, y exportar los recibos y archivos recuperados para verificarlos. La lectura con `qa` es evidencia de lectura del formato, no necesariamente de fidelidad visual completa o compatibilidad con la aplicación original.

La final requiere un Skill funcional y un vídeo público en YouTube con ejecución sobre el NAS, de menos de tres minutos y narración en inglés o subtítulos completos en inglés. El guion actual de 2:56 es una planificación; reservar más margen al montarlo y usar solo resultados observados. Exportar las evidencias antes del fin del acceso asignado, porque el dispositivo se reinicia para el siguiente participante.

## Criterio de cierre

Cerrar la iteración local cuando las ambigüedades estén resueltas, las regresiones pasen, las fixtures estén íntegras, el agente complete el ciclo de aprendizaje y el PDF/ZIP correspondan a la versión final. La candidatura de primera ronda puede prepararse con evidencia local declarada honestamente. La validación de final queda cerrada únicamente con la ejecución real y su vídeo.

Las mejoras de producto posteriores, como el plan mínimo de refuerzo o la memoria de emergencia independiente, pueden esperar a una versión posterior; el siguiente trabajo tiene un alcance de cierre definido.
