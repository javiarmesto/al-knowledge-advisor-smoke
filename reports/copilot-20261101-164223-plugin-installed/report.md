# Smoke test Copilot — plugin instalado a mitad de sesión

- Run id: copilot-20261101-164223-plugin-installed
- Repo commit: ad52e4ebacc9923095727a88413ffd6959ed40c9 (el informe va en la rama de la PR #1)
- Host: GitHub Copilot CLI 1.0.104 (observado). Modelo: NOT VERIFIED por el host.
- Fixture sha256 e7ece325…364c, sin modificar. Perfiles sin modificar.

## Plugin (evidencia del host)

- `copilot plugin install microsoft/BCQuality` -> `Plugin "bcquality" installed successfully. Installed 3 skills.` (aviso: instalación directa deprecada).
- `copilot plugin list` -> `bcquality (v1.9.0)`.
- Ruta: /root/.copilot/installed-plugins/_direct/microsoft--BCQuality; `plugin.json` version 1.9.0. Origen en config.json: github microsoft/BCQuality, instalado 2026-11-01T16:42:26Z.
- Commit cargado: NOT VERIFIED (directorio sin .git; se instaló la rama por defecto, sin pin). Lock: a56b272c… v1.9.0. La versión coincide; el commit no se puede comparar -> no declarar comparabilidad exacta con Claude.
- Hashes de contratos medidos por el orquestador (prefijos): entry.md 7914bedf, read.md f04df87c, do.md 77c75eb1, al-knowledge/SKILL.md 2b2d35fc. Coinciden con los que declaró el asesor.
- El plugin se instaló durante la sesión: el asesor informó que no tenía herramienta Skill y ejecutó el contrato inline.

## Delegación

La invocación `task` con agent_type al-knowledge-advisor devolvió un informe final (raw/dispatch.json; el texto narrativo completo del asesor no se guardó en archivo, solo sus bloques JSON en qN/response.json). Es evidencia del orquestador sobre la llamada; el host no exportó un registro de eventos. Una sola delegación cubrió las cuatro consultas.

## Consultas (preguntas exactas en qN/question.txt; JSON original en qN/response.json, sin reparar)

Los JSON son los que el propio asesor compuso, copiados tal cual del informe; no son salida nativa del host.
q2/response.json es inválido según el propio asesor (referencia conditional con `unknown` vacío y falta la segunda referencia citada). Se conserva sin reparar. No hay dispatch.json por consulta; ver raw/dispatch.json.
No se ejecutó validate_result.py: no hay reads.json de un recolector independiente.

## Criterios

| Criterio | Resultado | Nota |
| --- | --- | --- |
| Descubrimiento | PASS (parcial) | Plugin y agente disponibles según el host (`plugin list`, agente en la lista de tareas); carga a mitad de sesión |
| Delegación | NOT VERIFIED | Llamada `task` completada, pero sin evento exportado del host |
| Selección | PASS | 4 consultas focalizadas, sin inventar versión/país/auth/reintentos (declarado por el asesor, texto revisado por el orquestador) |
| Ejecución | NOT VERIFIED | Ejecución inline autoatestada; sin recolector de lecturas |
| Contrato independiente | NOT VERIFIED | Sin reads.json ni validador; q2 inválido por autoevaluación |
| Resultado | NOT VERIFIED | Outcomes y condiciones preservados; sin severidades ni aprobaciones; calidad semántica no verificada |
| Efectos | NOT VERIFIED | El asesor no escribió archivos según su declaración; no hay recolector del host |

Estado global: INCONCLUSO (sin PASS global). La PR anterior con BLOCKED se mantiene como historial.
