# Prompt para GitHub Copilot cloud (también se puede pegar desde móvil)

Ejecuta el smoke test desde la rama base seleccionada para esta tarea. Registra su commit y no cambies de rama durante la prueba. Lee AGENTS.md, docs/ACCEPTANCE.md y el fixture experiments/knowledge-advisor/smoke-issue.md.

Comprueba que se descubre el agente al-knowledge-advisor y que está disponible el plugin oficial BCQuality. Registra la versión, procedencia y ruta realmente cargadas; compara con bcquality.lock.json. La configuración del marketplace no demuestra que la revisión esté fijada. Si difiere, indícalo y no declares comparabilidad exacta con la referencia Claude.

Invoca explícitamente al-knowledge-advisor para analizar el fixture y formular hasta cuatro preguntas relevantes. Cada consulta debe terminar Skill/ejecución inline -> Entry -> acción -> lecturas completas -> respuesta antes de empezar la siguiente. Conserva las preguntas exactas, cada dispatch y cada respuesta original. No añadas PLUGIN_ROOT a las preguntas. No inventes versión de BC, país, autenticación ni política de reintentos.

Si el entorno no puede delegar, sigue el perfil inline y registra delegación como NOT VERIFIED: no lo presentes como prueba del subagente. Si falta el plugin, registra BLOCKED y no reconstruyas la skill.

Como sesión orquestadora, guarda un informe en reports/<identificador-único>/report.md y cada question.txt, dispatch.json y response.json real en una subcarpeta q1, q2, etc. No agregues salto final a question.txt si no forma parte de la pregunta. No modifiques el perfil, fixture, configuración, harness ni código para forzar un PASS. Conserva los registros originales que el host permita exportar; no fabriques transcripciones.

Como consumidor, ejecuta SIEMPRE scripts/validate_result.py sobre cada response.json con --question-file RUTA/question.txt --mode structure --plugin-root RUTA-DEL-PLUGIN. No necesita reads.json ni run-id. Lee docs/VALIDATION.md y guarda stdout/stderr y código de salida por separado, nunca sobre los originales. Si falta jsonschema, instala requirements.txt en un entorno Python de la tarea; si no puedes, registra el error sin inventar la ejecución del validador. Conserva también el texto completo devuelto por el asesor, si está disponible, y distingue ese texto de un registro nativo de eventos.

Evalúa todos los criterios como PASS, FAIL o NOT VERIFIED. Un incumplimiento estructural confirmado implica FAIL de aceptación aunque el outcome original sea completed; conserva ese original intacto. Si falta un recolector independiente de lecturas, indica self-attested y lecturas NOT VERIFIED, sin ocultar errores ya demostrados. Para la fase completa usa --mode full con evidencia fiable. Un validador ejecutado sobre evidencia inventada por el modelo no cuenta. Diferencia el esquema de la verificación semántica.

Permite que el host entregue estos archivos en su PR de tarea. No hagas merge, no cambies ajustes del repositorio y no publiques comentarios en otras issues o repositorios. El resultado puede ser inconcluso; nunca conviertas ausencia de evidencia en PASS.
