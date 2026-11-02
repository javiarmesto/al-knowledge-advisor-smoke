# Piloto de issues y PR con la semilla Barista Incidents

## Preparar el consumidor

Usar un repositorio de ensayo creado desde [AL-Go-PTE](https://github.com/microsoft/AL-Go-PTE/tree/99aa680a2af06a94b60c9fc9881aa2885681facc). La app procede de [04-brownfield-starter](https://github.com/javiarmesto/aldc-workshop-starters/tree/33a9cefda508f3c16e57fcc3339394f3b321a5ed/04-brownfield-starter). El importador toma el manifiesto y 25 fuentes AL de una copia local de esa semilla y comprueba cada archivo contra su blob Git. Los símbolos y las instrucciones de agentes del workshop quedan fuera del contexto del proyecto piloto. El manifiesto declara una dependencia de aplicación 28.0.0.0 y runtime 17.0. Registrar la versión del entorno si llega a conocerse.

Con Python 3 y Git, desde la carpeta de este paquete, indicar las rutas locales de la semilla y del consumidor nuevo:

```powershell
$seed = 'C:/Work/Projects/GitHub-BC-Audit/repos/aldc-workshop-starters/04-brownfield-starter'
$consumer = 'C:/Work/BCQuality/output/barista-advisor-pte'
$pack = (Get-Location).Path
python prepare_seed.py --seed $seed --consumer $consumer
git -C $consumer add -- App
git -C $consumer commit -m "Seed the AL-Go pilot with Barista Incidents"
```

En el consumidor de GitHub, la rama base debe contener esta app y el **host del asesor habilitado para ambos eventos**. Comprobar previamente que admite `issues.opened` y `pull_request.opened`, valida el objeto de GitHub, usa el perfil compartido de la PR #6 y pasa al asesor el resultado de `SetupBCQuality` del consumidor. Habilitar la skill `al-knowledge` en la política de prueba. Conservar el resultado como artefacto. Usar el mecanismo de autenticación autorizado para ese host. Presupuesto sugerido por evento: una pregunta, máximo 30 AI Credits por cada una de las dos sesiones. Dos eventos completos permitirían hasta 120 en total.

Este paquete prepara las **entradas** y el criterio de evaluación. La plantilla PTE, su revisor oficial y el workflow manual de snapshots del banco de pruebas no implementan por sí solos los dos disparadores del asesor. Mientras falte ese host, registrar la integración como **pendiente**. Preparar primero la rama base con un build AL-Go verde. No desplegar la app del piloto.

## A. Issue de diseño

Desde el navegador, abrir **Issues → New issue** en el consumidor. Pegar [el título](issue-title.txt) y [el cuerpo](issue.md) sin crear una rama de solución ni asociar una PR. Registrar la URL de la issue y la del run disparado por su apertura. Dejar que finalice antes de crear el segundo evento.

## B. PR de revisión

Desde la raíz del consumidor preparado, crear una rama de prueba. `$pack` apunta a esta carpeta del banco de pruebas.

```powershell
git switch -c pilot/barista-export-key
git apply --check "$pack/pr.patch"
git apply "$pack/pr.patch"
git diff --check
git add -- App/src/DataModel/BRISalesSetupExt.TableExt.al
git commit -m "Add export credential to Barista sales setup"
git push -u origin pilot/barista-export-key
```

En GitHub seleccionar **Compare & pull request** con destino a la rama base autorizada por el consumidor. Abrirla lista para revisión con [el título](pr-title.txt) y [el cuerpo](pr.md). Si ya se preparó la rama local con el campo, basta publicarla en el remoto del consumidor y abrir la PR. Registrar el SHA de head con `git rev-parse HEAD`. Mantener el cambio de prueba fuera de la rama base.

## Evaluar después de cada run

Mantener esta rúbrica y el parche de la PR fuera de los datos suministrados al asesor de la issue. La pregunta la selecciona el asesor. No exigir una redacción o un número de citas predeterminados.

| Comprobación | Issue | PR |
| --- | --- | --- |
| Identidad y aislamiento | Evento real del consumidor, número, título y reporte. Puede ejecutarse antes de existir una PR. | Evento real del consumidor, número, base y head verificados. El diff corresponde al SHA registrado. |
| Selección y utilidad | Identifica la decisión sobre almacenamiento, aporta orientación aplicable con cita y distingue la decisión pendiente sobre el alcance por empresa. Aprovecha que el reporte ya especifica clave de API y trabajo programado. | Señala el campo añadido `50901 "BRI Export API Key"; Text[250]` en `App/src/DataModel/BRISalesSetupExt.TableExt.al`. Explica la exposición potencial por lecturas de tabla y propone una alternativa citada. Evita atribuir al diff una página, un valor real o una filtración observada. |
| Plugin y contrato | En ambas entradas, registrar la política efectiva y la identidad del plugin preparado por `SetupBCQuality`, delegación, pregunta exacta, Entry por consulta, respuesta original, lecturas y salida del validador. | Verificar que los artículos citados pertenecen al contenido permitido y que los hashes corresponden a esa ejecución. |
| Criterio semántico del evaluador | La regla de referencia del corpus de los pilotos es `microsoft/knowledge/security/secrets-isolated-storage.md`. Se acepta una fuente equivalente si respalda la decisión. Revisar por separado cualquier afirmación sobre permisos de la Job Queue. | Comprobar que la recomendación cambia la decisión de almacenamiento en ese fragmento. Una cita genérica sobre autenticación no es suficiente. |

Registrar para cada caso el evento, objeto y commit cuando corresponda, URL del run, referencia del perfil, procedencia del plugin y enlace al artefacto. Anotar por separado el veredicto automático y la revisión semántica. Un `partial` puede ser útil con una recomendación respaldada. Si el filtrado elimina la cobertura o la skill está deshabilitada, conservar ese resultado. La ausencia de un evento o de evidencia de `SetupBCQuality` deja pendiente la prueba de integración incluso si el smoke manual pasa.

## Verificación de preparación

La base y la rama candidata compilaron localmente con AL Compiler 18.0.43.1464 y los símbolos BC 28 del workshop. El parche pasó `git apply --check` y `git diff --check`: un archivo de la app, cinco líneas añadidas. Esta comprobación valida los estímulos del piloto. Los resultados de los dos eventos se registrarán al ejecutar el host en GitHub.
