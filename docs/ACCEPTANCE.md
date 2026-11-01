# Criterios de aceptación

Cada ejecución identifica commit del repo, host/versión/modelo observado, perfil utilizado, fixture, plugin cargado, revisión/version y hashes de contratos cuando sea posible. Datos no observados quedan desconocidos.

| Criterio | Evidencia necesaria para PASS |
| --- | --- |
| Descubrimiento | Perfil real y plugin oficial disponibles en esa sesión; registrar origen de carga |
| Delegación | Evento del host que invoca al-knowledge-advisor y su terminación; leer el perfil no basta |
| Selección | Preguntas focalizadas y justificadas, hasta cuatro; sin inventar dimensiones ausentes |
| Ejecución | Invocación o ejecución inline del contrato oficial; un Entry por consulta y lecturas completas antes de la siguiente |
| Estructura y referencias | Esquema oficial, pregunta exacta, rutas y citas explícitas comprobadas por el consumidor; se ejecuta aunque falte reads.json |
| Contrato independiente | Respuesta original, pregunta exacta y validación con evidencia de lecturas recogida del host por un consumidor de confianza |
| Resultado | Preservar outcomes, condiciones, preguntas pendientes; sin severidades ni aprobaciones |
| Efectos | Asesor de lectura; solo el orquestador/harness escribe evidencias en el lugar acordado |

Usar FAIL ante una contradicción observada; NOT VERIFIED si falta evidencia; BLOCKED en el estado general si falta un requisito. No dar PASS global cuando un criterio requerido está NOT VERIFIED.

El resultado de la skill puede ser completed, partial, no-knowledge o failed. Entry puede devolver no-match o failed: mantener estos dispatch fuera del validador de knowledge-response.
No exigir que esta fixture produzca exactamente cuatro respuestas ni un partial concreto.
No-knowledge no prueba que no exista una regla. El esquema no prueba comprensión ni corrección semántica.
Los casos no-knowledge, Entry no-match/failed, precedencia y configuración de capas requieren fixtures adicionales; no se consideran cubiertos por esta prueba.

## Evidencia

- raw/: salida nativa del host, prompt y stderr originales.
- analysis/: preguntas exactas, JSON original por pregunta, evaluación y resultados del validador.
- manifest.json: identificador de ejecución, procedencia y límites.
- reads.json solo puede venir de un recolector externo que haya comprobado el resultado completo de las herramientas. El modelo NO lo genera.
- Para atribución inequívoca, leer otra vez un artículo compartido dentro de la consulta que lo cita.

Este repositorio incluye captura de stream-json de Claude y un wrapper del validador oficial. **No incluye todavía un recolector independiente compatible con los formatos de ambos hosts.** Guardar el stream no equivale a verificar sus lecturas. Hasta conectar/revisar ese recolector, las lecturas independientes permanecen NOT VERIFIED. Un incumplimiento estructural observado hace FAIL al contrato y a la aceptación global; no se oculta bajo NOT VERIFIED.

El informe Claude facilitado en la conversación usó un stand-in. Aquí se usa el perfil local real, copiado el 2026-11-01 (normalizando finales de línea), que ya contiene consultas secuenciales. Los adaptadores añaden el límite de cuatro preguntas y la relectura de citas compartidas. Esta revisión aún necesita ejecución real.

## Validación obligatoria del consumidor

Seguir [VALIDATION.md](VALIDATION.md) y ejecutar `--mode structure` para cada respuesta aunque no exista reads.json. Conservar JSON y salida del validador por separado. Un outcome original completed no prevalece sobre un FAIL de validación; nunca se reescribe para cambiarlo a failed. Si solo falta evidencia, mantener NOT VERIFIED.

Ejecutar el contrato inline es un modo permitido por BCQuality. Que el agente componga el knowledge-response no es por sí mismo una fabricación. El requisito es cumplir el protocolo, preservar su resultado y distinguir self-attestation de observación independiente.
