# Claude Code: ejecución reproducible

Requisitos: Git, Python 3.10+, Claude Code instalado y autenticado, acceso al modelo y red hacia GitHub/Anthropic. El plugin se carga para esa sesión desde la revisión fijada, sin modificar instalaciones globales. No requiere AL-Go ni tenant. PowerShell no es obligatorio: el asesor puede usar el fallback oficial Glob/Grep/Read.

Ejecutar desde una terminal externa a Claude Code:

```text
git clone https://github.com/javiarmesto/al-knowledge-advisor-smoke.git
cd al-knowledge-advisor-smoke
python -m venv .venv
```

Activar el entorno: en PowerShell, .venv\Scripts\Activate.ps1; en Linux/macOS, `source .venv/bin/activate`.

```text
python -m pip install -r requirements.txt
python scripts/check_setup.py
python scripts/prepare_plugin.py
claude --version
claude auth status
python scripts/run_claude.py --max-budget-usd 10 --max-turns 40 --timeout 900
```

Si tu sesión no tiene autenticación, completarla antes del runner. No poner credenciales en el repositorio. `--model` permite elegir explícitamente un modelo disponible en tu cuenta; registrar el modelo realmente utilizado en los eventos del host.

El runner conserva salida original en output/claude/<run-id>/raw/stream.jsonl, stderr, prompt y manifest. Quita CLAUDE_AUTO_BACKGROUND_TASKS y solicita tareas síncronas; verifica los eventos porque el comportamiento depende del host. El coste máximo es un límite solicitado al CLI, no una estimación de coste garantizada. No se inicia ninguna ejecución de pago automáticamente al hacer push.

El asesor es el perfil real del repositorio, no un stand-in. Usa herramientas de lectura/Skill; la sesión principal puede delegar. El runner no habilita shell ni escritura para el modelo. La escritura de evidencias la hace Python fuera del modelo.

La configuración global de Claude puede cargar otros plugins/hooks; revisar system/init y registrar conflictos. Si otra instalación bcquality ocupa el mismo nombre o no se observa la ruta fijada, marcar procedencia NOT VERIFIED y repetir en una sesión limpia. No reemplazar instalaciones globales silenciosamente. No ejecutar desde una sesión anidada ni eliminar sus protecciones.

## Validación del resultado

Primero preservar el texto final del subagente desde el registro del host y extraer, sin reparar, cada pregunta y respuesta original. Mantener Entry no-match/failed aparte. No pedir al agente principal que reemita todo el bloque: el stream es la evidencia original.

Un recolector externo debe comprobar lecturas completas exitosas y asignarlas a la consulta correcta; aún no se incluye ese recolector. Hasta entonces, contrato independiente = NOT VERIFIED. No crear reads.json a partir de las citas o declaraciones del modelo.

Una vez disponible la evidencia fiable, por consulta:

```text
python scripts/validate_result.py response.json --question-file question.txt --read-evidence reads.json --run-id ID-DEL-CONSUMIDOR --plugin-root .deps/bcquality
```

El comando devuelve el código del validador oficial: 0 válido, 1 inválido, 2 error de entrada/recurso. No altera el JSON. Un éxito valida contrato y evidencia aportada; no certifica comprensión ni todos los criterios de aceptación.

Para comparar con Copilot, usar el mismo fixture/perfil y comprobar la revisión realmente cargada. Una coincidencia de versión por sí sola no demuestra igualdad de contenido.
