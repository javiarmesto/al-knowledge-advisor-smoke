# AL Knowledge Advisor — smoke test

Banco de pruebas para comparar el asesor en GitHub Copilot y Claude Code usando la skill oficial `microsoft/BCQuality:al-knowledge`.

**Repositorio:** javiarmesto/al-knowledge-advisor-smoke  
**Rama de partida:** main

## Prueba con captura independiente

Usar el [runner SDK de Copilot](docs/RECORDED-COPILOT.md) para producir eventos nativos y reads.json. Incluye preflight sin llamadas al modelo, consultas aisladas y validación externa. El workflow manual necesita credenciales de Copilot configuradas por el usuario. La ejecución mediante chat que sigue abajo mantiene sus límites de evidencia.

## Ejecutar desde GitHub Mobile / Copilot cloud

1. Tener Copilot cloud agent habilitado para tu cuenta y acceso a este repositorio. El repositorio no puede habilitar tu suscripción ni permisos.
2. En la creación de una tarea de Copilot, seleccionar este repositorio y `main` como rama base si la interfaz muestra el selector.
3. Pegar el contenido de [prompts/copilot-smoke.md](prompts/copilot-smoke.md). Si aparece selector de agente, elige el predeterminado para que orqueste y delegue al asesor.
4. Revisar la sesión y los archivos de evidencia que entregue la tarea en su PR. La configuración del plugin está en `.github/copilot/settings.json`.
5. Evaluar con [los criterios](docs/ACCEPTANCE.md). Si falta plugin, acceso o evidencia, conservar BLOCKED / NOT VERIFIED.

Prompt breve equivalente:

> Lee prompts/copilot-smoke.md y ejecuta sus instrucciones. Usa el agente al-knowledge-advisor sobre el fixture del repositorio. Conserva resultados originales y evidencia; no modifiques el test para hacerlo pasar.

## Claude Code

[Preparación y ejecución automatizada](docs/CLAUDE.md). El runner captura el stream original y limita coste, turnos y tiempo. Usa el plugin fijado en [bcquality.lock.json](bcquality.lock.json), cargado para la sesión mediante `--plugin-dir`.

## Qué está automatizado

- Preparación de una copia oficial de BCQuality fijada por commit.
- Comprobación de archivos/configuración y compilación de scripts, también en GitHub Actions.
- Lanzamiento de Claude Code y captura de salida, stderr y metadatos.
- [Validación estructural independiente](docs/VALIDATION.md), sin exigir evidencia de lecturas para detectar respuestas inválidas.
- Validación completa mediante el consumidor oficial cuando existe evidencia fiable de lecturas.
- Regresión con el q2 original de la PR #1 y comprobación automática de los informes guardados.

**Una comprobación de setup verde no es un smoke test del agente.** El runner SDK incorpora el recolector; su funcionamiento con el modelo debe verificarse en una ejecución autenticada. Las tareas de chat sin ese runner no generan automáticamente sus evidencias; los registros incompletos permanecen NOT VERIFIED y los incumplimientos observados dan FAIL. No se ha ejecutado aquí una consulta real al modelo como parte de la creación del repositorio.

No requiere tenant BC, extensión AL compilable ni AL-Go. La integración con AL-Go será una segunda fase sobre esta base. No contiene datos reales ni modifica aplicaciones.

## Fuentes de configuración

- [Plugins de Copilot cloud](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/configuring-agent-settings)
- [Agentes de Copilot](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Claude Code programático](https://code.claude.com/docs/en/headless)
- [Contrato oficial de validación](https://github.com/microsoft/BCQuality/blob/a56b272c6b950c2a423bbeda190585cd53beca2a/docs/knowledge-response-validation.md)

El marketplace de Copilot puede cargar una revisión distinta de la fijada para Claude. Registrar esa diferencia; no afirmar comparabilidad exacta solo por el nombre o versión del plugin.
