# Smoke AL Knowledge Advisor (Copilot) — copilot-20261101-1733-structure

**Estado global: NOT VERIFIED** (no PASS global; la estructura es válida pero faltan lecturas independientes, delegación observada por evento del host y procedencia exacta).

- Commit del repo: `80812659b159efdcedbc03676112863d6e57bca3` (rama base `fix/independent-structure-validation`; rama de trabajo `special-train` en el mismo commit).
- Host: GitHub Copilot CLI 1.0.104. Orquestador: claude-sonnet-5.5. Modelo del asesor: no observado.
- Fixture y perfil: ver `manifest.json` (hashes).

## Plugin (paso 1-2)
- No estaba instalado al empezar la sesión (`~/.copilot/installed-plugins/` vacío). Instalado en esta tarea: `copilot plugin marketplace add microsoft/BCQuality` y `copilot plugin install bcquality@bcquality` (éxito; ver `raw/plugin-install.txt`).
- Versión cargada: 1.9.0; ruta `/root/.copilot/installed-plugins/bcquality/bcquality`; `source_sha` de config `b425b3ee…` (no es commit git; la caché no tiene `.git`).
- Lock: versión 1.9.0 (coincide), commit `a56b272c…`. **Revisión real: desconocida**; coincidir en versión no prueba igualdad de revisión. Sin comparabilidad exacta con la referencia Claude.
- La herramienta Skill de bcquality no estaba expuesta en esta sesión (instalación posterior al arranque) → ejecución inline.

## Criterios
| Criterio | Estado | Nota |
| --- | --- | --- |
| Descubrimiento | NOT VERIFIED | Perfil `al-knowledge-advisor` resuelto por el host (`task`), plugin instalado en disco; carga en la sesión no demostrada por evento del host. |
| Delegación | NOT VERIFIED | Se usó `task` con agent_type al-knowledge-advisor y devolvió resultado, pero no hay registro nativo de eventos exportado. |
| Selección | PASS (revisión humana) | 4 preguntas focalizadas, sin inventar versión BC, país, autenticación ni reintentos. |
| Ejecución | NOT VERIFIED | Inline, secuencial según el asesor (self-attested). El dispatch de Entry fue **reconstruido** por el asesor (idéntico en q1–q4), no registrado por consulta. |
| Estructura y referencias | PASS | `validate_result.py --mode structure` en q1–q4: schema, question, paths y answerCitations PASS; código de salida 0. |
| Contrato independiente | NOT VERIFIED | Sin recolector; reads.json no generado. Las lecturas listadas por el asesor son self-attested. |
| Resultado | PASS | Los 4 outcomes `completed` preservados sin cambios; sin severidades. |
| Efectos | NOT VERIFIED | El asesor declara no haber escrito archivos; el perfil no impone sandbox. `git status` solo muestra reports/ nuevo. |

contractStatus y smokeStatus del validador: NOT VERIFIED en las cuatro respuestas.

## Preguntas (exactas en `qN/question.txt`)
1. Almacenamiento y manejo de la credencial API en AL.
2. Guía del job queue handler con exportación HTTP y reejecución.
3. Guía previa al envío de datos de cliente a un servicio externo.
4. Gestión del resultado de HttpClient (fallos, status, transacciones de escritura).

## Evidencia
- `qN/{question.txt,dispatch.json,response.json}`: originales sin modificar.
- `analysis/qN.validator.{stdout.json,stderr.txt,exitcode.txt}`: validación por separado (exit 0, stderr vacío).
- `raw/`: prompt de delegación, texto devuelto por el asesor (narrativa; los bloques JSON están en los archivos qN) y registro de instalación.
- Límite: el texto del asesor y el dispatch no son un registro nativo de eventos del host.
