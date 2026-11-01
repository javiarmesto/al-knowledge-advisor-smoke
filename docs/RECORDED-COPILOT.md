# Copilot con captura externa

Este runner usa el SDK oficial 1.0.28 y el perfil canónico real del asesor. Es un **adaptador SDK con herramientas de lectura instrumentadas**, no una certificación del runtime de GitHub Mobile. El plugin oficial se prepara desde el commit de bcquality.lock.json antes de iniciar Copilot. No se instala a mitad de sesión ni se depende del marketplace.

## Requisitos

- Node.js 22.12+; Git; Python 3.10+ y requirements.txt.
- Acceso a un modelo de Copilot y credenciales disponibles para el runtime. El runner puede usar un login de gh accesible o COPILOT_SMOKE_TOKEN; nunca copies el token al prompt, a archivos versionados o a informes.
- Red para descargar el SDK/runtime oficial, BCQuality y para acceder a Copilot.
- Seleccionar un modelo real de tu cuenta. No se fija un modelo inventado o retirado.

Desde el checkout de la rama feat/copilot-recorded-runner:

```text
python -m pip install -r requirements.txt
python scripts/prepare_plugin.py
npm install
npm test
npm run check:sdk
node scripts/run_copilot.mjs --offline-check
node scripts/run_copilot.mjs --preflight
```

Si usas un venv, actívalo primero o indica `--python RUTA-AL-PYTHON` al runner. Cada intento crea su carpeta propia bajo output/copilot/.

- offline-check verifica el pin y cada blob Git, importa el SDK y comprueba jsonschema. No inicia el runtime.
- preflight inicia el runtime y verifica autenticación; no manda prompts al modelo. BLOCKED por falta de credenciales es un resultado explícito, no un test del agente.
- run envía prompts y consume créditos. Solo ejecutarlo después de superar preflight:

```text
node scripts/run_copilot.mjs --run --model ID-REAL-DEL-MODELO --max-questions 1 --max-credits 5 --timeout 600
```

Primero una pregunta; ampliar a 2–4 solo cuando la primera produzca eventos y evidencias válidos. El límite de créditos se solicita por sesión: una fase de selección más una sesión por pregunta. Con una pregunta y 5 créditos por sesión, el límite solicitado total es 10 AI Credits, no 10 USD. La aplicación de ese límite corresponde al runtime. También se acotan tiempo por sesión y número de turnos.

## Qué registra el host

1. Un plan de preguntas formulado por el asesor, preservado como string original. El host asigna una sesión nueva a cada pregunta.
2. Eventos nativos mediante onEvent registrado al crear la sesión, incluida delegación. Las llamadas sin atribución de subagente no se aceptan.
3. El Entry original se envía a smoke_dispatch antes de cualquier cuerpo de artículo. Una captura tardía o una segunda sustitución se rechaza. Esto acredita momento y transporte; no prueba que el razonamiento de routing fuera correcto.
4. smoke_read sirve bytes de un snapshot inmutable del plugin. Su lectura solo cuenta si el evento tool.execution_complete confirma éxito, identidad de herramienta/subagente y el mismo contenido exacto en result.content. detailedContent de interfaz no basta.
5. El JSON original de respuesta se captura una vez, sin reparación. La validación completa se ejecuta en Python fuera del modelo.

El runtime solo expone task y las herramientas instrumentadas; el agente por defecto no recibe las herramientas de captura, por lo que debe delegar. El asesor no recibe shell, edición, web ni mensajería. Las escrituras de evidencias las hace el host en output/. Es una restricción de herramientas, no una afirmación de aislamiento del sistema operativo.

## Artefactos

- manifest.json: commit del repo, SDK, perfil, fixture, adaptación, límites y hashes de todos los archivos del plugin comprobados contra sus blobs Git.
- plan/raw/events.jsonl y qN/raw/events.jsonl: objetos de eventos nativos sin resumir.
- raw/message-N.json: mensajes completos, manteniendo sus bloques JSON.
- raw/calls.jsonl y raw/read-N.txt: invocaciones recibidas y cuerpos exactos enviados.
- qN/dispatch.json, task-context.json, question.txt y response.json: originales y contexto ligado por el host.
- qN/reads.json: generado exclusivamente desde lecturas confirmadas de esa consulta.
- qN/read-exclusions.json: lecturas que no pueden acreditarse.
- qN/validation.*: salida y código del consumidor oficial.
- summary.json: veredicto automatizado separado de semanticReview.

Un automatedSmokeStatus PASS acredita los checks automatizados documentados: delegación, captura en orden, entrega íntegra de citas, pin y contrato. No certifica la interpretación de cada artículo ni la calidad de selección de preguntas. semanticReview queda separado. Una fase incompleta no se convierte en PASS.

Los tests del recolector usan eventos **sintéticos**. Un CI verde prueba el código y la compatibilidad de tipos/preflight, no que una sesión de modelo haya completado el flujo. Si el runtime cambia el formato o trunca contenido, se excluye la lectura y el resultado no se acepta.

## GitHub Actions / móvil

El workflow Recorded Copilot smoke es manual y no se ejecuta al hacer push. Necesita el secret COPILOT_SMOKE_TOKEN con acceso a Copilot; el token estándar GITHUB_TOKEN del workflow no sirve para inferencia. La configuración de credenciales no se incluye en esta PR.

Una vez integrado el workflow en la rama predeterminada, se puede lanzar desde Actions seleccionando la rama y el modelo. La UI móvil puede variar; el punto de ejecución es el workflow, no un prompt de chat. Mientras la PR no esté integrada, usar el runner local; no prometer que workflow_dispatch aparezca en la interfaz.

El workflow sube solo evidencias seleccionadas; no sube runtime-home ni configuración de autenticación. Conservar los logs localmente durante revisión y evitar publicar información privada. Esta fixture contiene solo datos sintéticos.

## Referencias

- https://github.com/github/copilot-sdk/releases/tag/v1.0.28
- https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events
- https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents
- https://github.com/microsoft/BCQuality/blob/a56b272c6b950c2a423bbeda190585cd53beca2a/skills/al-knowledge/SKILL.md
