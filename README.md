# AL Knowledge Advisor — smoke test

Banco de pruebas para comparar el asesor en GitHub Copilot y Claude Code usando la skill oficial `microsoft/BCQuality:al-knowledge`.

**Repositorio:** javiarmesto/al-knowledge-advisor-smoke  
**Rama de partida:** main

## Encaje previsto en AL-Go

El asesor se propone para las **issues y pull requests del propio proyecto AL que usa AL-Go**. Ambas entradas usan el mismo perfil y el mismo contrato de consulta a `al-knowledge`.

| Entrada | Contexto que prepara el host | Resultado para el mantenedor |
| --- | --- | --- |
| Issue | Repositorio y número, título, descripción, comentarios relevantes y evidencias disponibles, incluso antes de que exista una PR. | Orientación sobre el problema o la decisión de diseño, con citas cuando haya cobertura y una comprobación concreta para resolver lo pendiente. |
| Pull request | Repositorio y número, rama base, commit revisado, diff y contexto de los cambios AL. | Orientación sobre una decisión del cambio, vinculada al archivo y fragmento correspondiente para el revisor. |

El [escenario oficial de revisión de PR](https://github.com/microsoft/AL-Go/blob/adb81ccf121dfbf1de8fe4ae2da7e7474528bed9/Scenarios/Agents/CopilotCodeReview.md) es la referencia para separar la recepción del evento, el runner de confianza y la publicación. En el diseño propuesto, el host comprueba la activación en el repositorio y recupera el objeto de GitHub correspondiente. Para una PR comprueba además la base, el head y la elegibilidad para revisión. Para una issue comprueba su identidad y obtiene el contexto de la conversación. `SetupBCQuality` prepara el plugin filtrado según la política del proyecto. El asesor recibe el contexto saneado y devuelve su informe al host, que controla cualquier publicación. Las credenciales del marketplace privado quedan limitadas a la instalación.

Los pilotos con las issues #2267 y #765 de `microsoft/AL-Go` probaron la consulta de conocimiento con copias de informes públicos. Para validar la integración en un proyecto consumidor quedan dos pruebas: una issue del proyecto sin PR asociada y una PR con un diff AL. En ambas habrá que comprobar el disparador, la política efectiva y el uso del plugin preparado por `SetupBCQuality`.

## Escenarios en un proyecto consumidor

[Issue y PR sobre la semilla Barista Incidents del workshop](scenarios/workshop-barista/README.md). Incluye el material que se entrega al asesor, un parche AL aplicable y la rúbrica para evaluar ambos eventos.

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
