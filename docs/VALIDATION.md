# Validación en dos fases

Ejecutar las comprobaciones fuera del asesor, sobre los archivos originales. No reparar respuestas ni generar reads.json a partir de declaraciones del modelo.

## 1. Estructura y comprobaciones estáticas: siempre

```text
python scripts/validate_result.py response.json --question-file question.txt --mode structure --plugin-root .deps/bcquality
```

No requiere reads.json ni run-id. Usa el esquema oficial del corpus indicado y comprueba:

- JSON estricto (incluidas claves duplicadas y constantes no JSON).
- Esquema completo y pregunta idéntica, incluidos espacios y finales de línea.
- Rutas existentes y canónicas de references/suppressed.
- Rutas completas explícitas citadas en answer que falten en references.

La última comprobación no interpreta el texto ni resuelve citas abreviadas como `…/archivo.md`. No prueba que cada afirmación esté sustentada. La existencia en el corpus de validación no demuestra que fuera el corpus cargado durante el test.

La salida separa cada check, contractStatus y smokeStatus. Un fallo observado da FAIL, aunque falten trazas. Si las comprobaciones pasan pero no hay verificación completa, contractStatus y smokeStatus siguen NOT VERIFIED. Conservar el resultado JSON del validador en un archivo distinto a response.json.

## 2. Contrato con lecturas: cuando haya evidencia fiable

```text
python scripts/validate_result.py response.json --question-file question.txt --mode full --read-evidence reads.json --run-id ID-DEL-CONSUMIDOR --plugin-root RUTA-DEL-PLUGIN-UTILIZADO
```

Primero ejecuta las comprobaciones estáticas. Solo después llama al validador oficial. Si la respuesta tiene citas y no se aporta evidencia, devuelve NOT VERIFIED; nunca genera un manifiesto para completar el requisito.

Las respuestas sin referencias (por ejemplo no-knowledge) no necesitan un manifiesto de lecturas, aunque la invocación completa requiere run-id. El resto de criterios del smoke siguen pendientes.

| Código | Significado |
| --- | --- |
| 0 | Pasaron los checks solicitados. En modo structure NO es aceptación completa. |
| 1 | Incumplimiento observado: FAIL. |
| 2 | Error de entrada, dependencia o recurso; no demuestra ejecución válida. |
| 3 | Estructura correcta, pero modo full sin evidencia de lecturas requerida: NOT VERIFIED. |

Incluso contractStatus PASS deja smokeStatus NOT VERIFIED: delegación, procedencia y corrección semántica requieren evidencia adicional. El validador confía en el recolector; no determina por sí solo si un manifiesto es auténtico.

## Informes guardados y CI

```text
python scripts/validate_saved_reports.py
python -m unittest discover -s tests -v
```

CI revisa todos los pares reports/**/q*/response.json + question.txt presentes en la rama y conserva report-structure-validation como artifact. Una respuesta inválida hace fallar ese paso. Si no hay respuestas, informa NOT RUN. Esta revisión usa la revisión fijada en bcquality.lock.json: es una auditoría retrospectiva contra esa referencia, no una certificación del plugin cargado.

La fixture tests/fixtures/copilot-q2 conserva los bytes originales de q2 de la PR #1. Las variantes y manifests creados por los tests son sintéticos y no aportan evidencia de lectura sobre aquella ejecución.
