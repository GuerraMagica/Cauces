# Contribuir a Cauces / Contributing to Cauces

Puedes ayudar con errores reproducibles, documentación, diseño, pruebas y mejoras
del código. Para empezar, abre un issue que explique el problema o un pull request
pequeño y enfocado. Describe el resultado esperado, el cambio y las comprobaciones
ejecutadas. Separa resultados comprobados de hipótesis o pruebas pendientes.

## Licencia y procedencia

Las nuevas aportaciones propias a código, documentación y artwork se realizan bajo
**GPL-3.0-only**, con el alcance y las excepciones de [LICENSE_SCOPE.md](LICENSE_SCOPE.md).
Conservas tus derechos; no se exige ceder la propiedad ni firmar un CLA separado.

Cada commit nuevo aportado al proyecto debe incluir un `Signed-off-by` mediante
`git commit -s`, usando tu identidad y un correo que puedas hacer público.
Con ese sign-off certificas el [Developer Certificate of Origin 1.1](DCO):
has creado la aportación o tienes derecho a entregarla bajo la licencia indicada.
El nombre, el correo y el sign-off pasan a formar parte del historial público.
Un sign-off es una declaración de procedencia, no una firma criptográfica.

El DCO se aplica a futuras contribuciones. No se han añadido sign-offs a commits
históricos ni se considera que la declaración del titular sustituya el DCO de
otros autores. El mantenedor revisa el sign-off al aceptar cambios; no se ha
instalado una integración automática de DCO.

Identifica las partes copiadas o adaptadas y conserva sus licencias/atribuciones.
Antes de incorporar una dependencia o un asset, documenta origen, licencia y
compatibilidad. El sign-off no concede derechos que el contribuyente no tenga.
Si utilizas IA, revisa el resultado y declara su uso y cualquier fuente o
limitación conocida; sigues siendo responsable de poder aportar el contenido.
No presentes código generado como una garantía de procedencia o de corrección.

## Audio y modelos

Usa ejemplos pequeños y sintéticos. No adjuntes voces de actores, audio de
producción, documentos internos, credenciales ni material de terceros sin permiso.
Describe incidencias de audio con formato, sample rate, canales, pasos e intervalos
de muestras o timecode cuando ayuden; nunca necesitas enviar material confidencial.

No añadas modelos ni pesos para los que no exista permiso aplicable. La licencia
de Cauces no se extiende a esos assets. No retires verificaciones de hashes como
atajo para cargar otros modelos. Cauces y MULTI SPEAKER SEPARATION LAB son
proyectos independientes.

## Cambios y comprobaciones

Consulta [README](README.md#compilar-y-verificar) para preparar las dependencias
y compilar. Después ejecuta `bash tests/run_public_tests.sh` para la arquitectura
del proceso actual, o indica `arm64`, `x86_64` o `all` explícitamente. Este recorrido
incluye CTest, cinco suites Swift y pruebas sintéticas de WAV/protocolo sin modelos
ni capturas privadas. Las dependencias de compilación sí son necesarias.

`bash tests/run_integration_tests.sh` requiere modelos y capturas locales no
publicados; un requisito ausente produce error, no una omisión silenciosa.
`run_security_tests.sh` conserva el recorrido completo de ambas categorías y,
por defecto, ambas arquitecturas. No se exige obtener ni subir assets privados
para proponer cambios revisables sin ellos. Indica el comando, qué has ejecutado
y qué queda pendiente, incluida la arquitectura real o Rosetta. Un fallo de
`sandbox-exec` debido al entorno se registra como fallo, no como PASS.

Mantén los cambios acotados. Para procesamiento de audio, comprueba los contratos
de muestras, canales, frecuencia y BWF correspondientes. Conserva el procesamiento
local y los permisos de App Sandbox; propone y explica cualquier cambio de
seguridad antes de modificarlo. Una prueba sintética no sustituye la escucha
profesional ni la validación en Pro Tools.

## English

Issues and focused pull requests are welcome for bugs, documentation, artwork,
tests and code. Explain expected behaviour, the change and actual validation.

Original contributions use **GPL-3.0-only** under [LICENSE_SCOPE.md](LICENSE_SCOPE.md).
You retain your rights; no copyright assignment or separate CLA is required.
Sign off each new contributed commit with `git commit -s` to certify the
[DCO 1.1](DCO). Use an identity and email you can make public: the sign-off becomes
part of permanent public history. This is a provenance declaration, not a
cryptographic signature. Historical commits have not been retroactively signed
off. Sign-offs are checked by the maintainer; no automated DCO integration is
installed.

Disclose copied/adapted material and AI assistance, review the result, retain
applicable notices, and verify your right to contribute. A sign-off cannot grant
rights you do not hold. Document the origin and compatible licence of dependencies
and assets before introducing them.

Use small synthetic examples. Do not upload confidential audio, actor voices,
internal documents, secrets or unlicensed models/weights. Do not bypass model
integrity checks or import the separate LAB's engines. Follow the build/test
instructions in README and report what actually ran; some integration tests
depend on unpublished local assets. Preserve audio contracts, local processing
and App Sandbox. After building with the development dependencies, run
`bash tests/run_public_tests.sh [arm64|x86_64|all]`: the default is the current
process architecture. This runs CTest, five public Swift suites, and synthetic
WAV/protocol checks without models or private reference captures. Missing tools,
builds, skipped CTests or test failures cannot produce a public PASS.
`run_integration_tests.sh` separately requires local authorised assets;
`run_security_tests.sh` remains the full public+integration command, defaulting
to both architectures. Report environment failures, including `sandbox-exec`,
rather than silently skipping tests. Synthetic checks do not establish
professional listening or DAW acceptance.
