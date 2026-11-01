# Smoke test Copilot — estado general: BLOCKED

- Run id: copilot-20261101-163412-blocked
- Repo commit: ad52e4ebacc9923095727a88413ffd6959ed40c9 (rama refactored-funicular)
- Host: GitHub Copilot CLI 1.0.104 (observado). Modelo: declarado por el modelo como claude-sonnet-5.5; NOT VERIFIED por el host.
- Fixture: experiments/knowledge-advisor/smoke-issue.md sha256 e7ece3259e01955ac6a7f3df263ceec257f52dd6c8eba53fc39d3673b8b4364c (no modificado)
- Perfil: .github/agents/al-knowledge-advisor.agent.md sha256 0e90ee4b…8739fe; experiments/…agent.md sha256 10e15eb0…aa93 (no modificados)

## Comprobaciones del host (ver raw/checks.txt)

- `copilot plugin list` -> "No plugins installed." (solo built-in browser-use disabled).
- ~/.copilot/installed-plugins vacío; no existe ninguna ruta bcquality en el sistema; .deps no existe.
- Skills visibles: ninguna `al-knowledge`.
- .github/copilot/settings.json declara marketplace bcquality y `bcquality@bcquality: true`, pero eso es configuración, no prueba de carga ni de revisión fijada.
- La instalación intentada en la sesión anterior no persiste.

## Comparación con bcquality.lock.json (commit a56b272c…, v1.9.0)

Versión, ruta y procedencia cargadas: ninguna (plugin no cargado). Comparación imposible: NOT VERIFIED.

## Criterios

| Criterio | Resultado | Nota |
| --- | --- | --- |
| Descubrimiento | NOT VERIFIED | El host lista el agente al-knowledge-advisor; plugin oficial ausente -> BLOCKED |
| Delegación | NOT VERIFIED | No se delegó: sin al-knowledge la skill no puede ejecutarse; no se reconstruye |
| Selección | NOT VERIFIED | No se formularon consultas (q1..q4 no existen) |
| Ejecución | NOT VERIFIED | Sin Skill/Entry/lecturas |
| Contrato independiente | NOT VERIFIED | Sin respuestas; sin recolector independiente |
| Resultado | NOT VERIFIED | Sin respuestas |
| Efectos | NOT VERIFIED | Solo se escribieron evidencias de este informe; sin cambios al fixture/agentes/harness (observación del orquestador) |

No hay question.txt, dispatch.json ni response.json porque no ocurrió ninguna consulta; no se fabricó nada. No se respondieron consultas ni se reconstruyó la skill. Tampoco es comparable con la referencia Claude.

Para desbloquear: `copilot plugin install` de microsoft/BCQuality fijado a a56b272c… en la misma sesión y repetir.
