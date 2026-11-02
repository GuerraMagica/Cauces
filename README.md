# Cauces — beta personal 0.4.2

App local para macOS 15 o posterior, con ejecutables universales ARM64/Intel.
Separa dos voces y un residual con **Cauces Multi-Speaker Separation ONNX v1
(selective FP16)** y una implementación propia del DSP. Interfaz SwiftUI; inferencia CPU con ONNX
Runtime 1.31.1; no requiere Python, cuentas ni conexiones durante el uso.

Este repositorio publica **código fuente, pruebas y documentación**. Los
modelos, pesos, audios, capturas del original, herramientas de investigación
y paquetes `.app`/ZIP no se distribuyen aquí. Los resultados documentados
proceden de la validación local; no equivalen a pruebas ejecutadas por GitHub.

La versión 0.3 incorpora el diseño Flow, textos propios en inglés y el icono Cauces.
Los assets editables y la guía de entrega están en `design/cauces-v1/START-HERE.md`.
Las teclas ⌘1–⌘4 cambian de pista y Espacio reproduce o pausa.

La versión 0.4.1 corrige la apertura de WAV al trasladar la app: el lector usa
el descriptor verificado directamente, sin reabrir `/dev/fd`. Los modelos y el
procesamiento numérico conservan los mismos bytes que 0.4.0. La reproducción
del error bajo una restricción controlada está verificada; la confirmación en
el Intel físico del usuario sigue pendiente.

## Uso

1. Abre `dist/Cauces-0.4.2/Cauces.app` con doble clic.
2. Abre o arrastra un WAV mono o dual mono idéntico: PCM16, PCM24 o float32,
   entre 8 y 48 kHz, hasta 30 minutos.
3. Pulsa **Separate voices**. Puedes cancelar; se descartan los resultados de ese
   trabajo y sus temporales. Solo se procesa un archivo a la vez.
4. Reproduce y cambia entre Original, Voice 1, Voice 2 y Residual. Las cuatro pistas
   comparten reloj y cursor; no hay normalización automática.
5. **Export audio…** crea `<nombre>_separated` en la carpeta que elijas.
   Contiene tres WAV float32 con mismo sample rate, muestras y canales. Una
   carpeta final existente provoca un error; no se sobrescribe.

Si el original tiene BWF, se conserva `time_reference` en muestras. No se
promete retención completa de iXML, UMID, historial, loudness o metadata
propietaria. El residual puede contener diálogo; las etiquetas de hablante son
estimaciones y pueden cambiar cuando la evidencia de solapamiento es débil.
No incluye estéreo real, batch, plugins de DAW ni procesamiento en tiempo real.

## Settings de reproducción

Abre **Cauces → Settings…** (⌘,). **Output** selecciona una salida Core Audio
solo para Cauces; **System Default** sigue la salida del sistema sin modificarla.
**Sample rate** ofrece valores compatibles con el dispositivo. **Device default**
sigue su reloj sin solicitar otro valor. **Apply** pausa la escucha, conserva el
cursor y la pista seleccionada, verifica el resultado y guarda la selección por
UID. **Cancel** descarta los cambios de la ventana.

Una frecuencia explícita cambia el reloj compartido del dispositivo y puede
afectar a otras apps. Una solicitud rechazada o que se revierte no se guarda;
se intenta restaurar el clock anterior si Cauces lo cambió. Si falla esa
restauración, el error lo indica. Los originales, la separación y los WAV
exportados conservan su formato y sample rate; este ajuste solo afecta a escucha.
La selección se recuerda al reiniciar, pero el reloj solo se escribe con Apply.
Si otra aplicación cambia la frecuencia, se requiere volver a aplicarla. Si se
desconecta una salida elegida expresamente, se pausa sin pasar silenciosamente a
los altavoces. No se incorporan ajustes de entrada, MIDI ni buffer.

En este equipo se verificaron 44,1/48 kHz en Audio Bridge 2-A, también bajo
Rosetta, y 48 kHz en los altavoces integrados. Estos últimos revirtieron varias
solicitudes de 44,1 kHz, incluso en una prueba independiente sin reproductor ni
App Sandbox: se comprueba el rechazo seguro; su causa no está identificada.
La compatibilidad efectiva de otros dispositivos/frecuencias depende del driver.

## Trasladarla al Intel

Copia la app completa o el ZIP personal, descomprímelo y abre la app. Incluye
sus modelos y runtime de cada arquitectura; no necesita otra aplicación
ni un entorno de desarrollo. Firma ad hoc local; no está notarizada
ni distribuida mediante Developer ID. No se han cambiado protecciones del
sistema. La apertura en el Intel físico debe comprobarse allí; Rosetta no
valida Sequoia ni su rendimiento.

Prueba primero una copia de un diálogo corto que puedas usar localmente:
abrir, separar, alternar pistas, buscar un punto, cancelar otro trabajo y
exportar. Reabre los tres archivos WAV en tu DAW para confirmar alineación y BWF.
Escucha respiraciones, consonantes, solapamientos, colas y matices del acting.
La aceptación auditiva profesional requiere esa escucha y no se deduce del
corpus sintético. No se afirma compatibilidad Pro Tools sin esa prueba.

## Código y API

- `src/dsp.*`, `src/pipeline.*`: matemática y separación sin UI ni archivos.
- `src/models.*`: sesiones ONNX Runtime CPU, formas y valores finitos.
- `src/separator.h`, `src/api.cpp`: API C pública y biblioteca compartida.
- `src/wav.*`, `src/scratch.*`: WAV, BWF, almacenamiento temporal y límites.
- `src/worker.cpp`: proceso persistente, protocolo acotado y exportación de CLI.
- `src/security.*`, `src/PrivateDirectory.swift`: temporales privados y copia/publicación verificadas.
- `src/LocalFilePolicy.swift`: rechazo de ubicaciones de nube/red reconocidas.
- `src/*.swift`: interfaz, estado de trabajos, transporte y preescucha.

`ds_create(model_dir, threads, error, capacity)` crea un contexto; `ds_separate`
recibe float32 planar `[canales,muestras]` y tres buffers de salida de igual
tamaño. Devuelve 0 al terminar o 1 con diagnóstico UTF-8. El callback de
progreso devuelve 0 para cancelar. No modifica salidas si falla. El contexto
es de un solo hilo; no destruirlo durante una llamada. `ds_destroy` libera
sesiones. Para silencio puede usarse contexto NULL. La biblioteca C no lee
ni escribe audio: sus adaptadores quedan fuera de la API numérica.

## Compilar y verificar

Requiere macOS, las herramientas de desarrollo Apple, CMake y Ninja. La
compilación no necesita los modelos; para procesar y empaquetar debes disponer
localmente de los archivos del modelo correspondientes a esta versión:
`separator.onnx`, `refiner.onnx`, `separator_gpu.onnx`, `weights.bin` y
`manifest.json`. No se descargan modelos ni se incluyen sus pesos en Git.
`scripts/package.sh` acepta `CAUCES_MODEL_DIR` para indicar tu copia local
autorizada; por defecto usa `vendor/cauces-models/`. El empaquetador aplica el
nombre de integración sin cambiar tensores. Los hashes permitidos están fijados
en `src/model_assets.cpp` y se comprueban tanto en el worker como en la API C.
Las sesiones utilizan los mismos bytes verificados, sin reabrir archivos.

Herramientas usadas en este equipo: Swift/Clang del SDK macOS 26.5, CMake y
Ninja existentes. Target de despliegue 15.0. No se instalaron herramientas
globales. Los modelos se copian desde su ubicación local; no se modifican.

El runtime ARM64 procede del paquete oficial 1.31.1. El runtime x86_64 se
compila desde `v1.31.1`, commit
`6af1a932e2286d5c58166085d24c68783033edee`; configuración y hashes en
`scripts/prepare-runtime.sh`. CMake descarga las dependencias fijadas
por ese proyecto dentro del build. Este paso de desarrollo usa red; la app
terminada no la necesita.

```sh
bash scripts/prepare-runtime.sh   # desarrollo: descarga y compila dependencias
bash scripts/build.sh
ctest --test-dir build/arm64 --output-on-failure
ctest --test-dir build/x86_64 --output-on-failure
bash scripts/package.sh
```

El empaquetador se niega a reemplazar una app ya existente. Mueve tu build
anterior antes de repetirlo. Las siete suites CTest y `tests/JobStateTests.swift`
no necesitan modelos ni audios externos durante su ejecución. Los tests Python
de comparación, worker y paquete, y `WorkerConnectionTests.swift`, son pruebas
de integración local: necesitan los modelos, un Python con NumPy cuando
corresponda y un corpus local de capturas CPU, que no se publica.
`CAUCES_REFERENCE_FIXTURES_DIR` indica su directorio (predeterminado:
`build/reference-fixtures/`); los adaptadores de comparación están en este repo. Esos tests no forman parte de la app de destino ni se presentan
como reproducibles con este repositorio por sí solo.

Las regresiones de seguridad se ejecutan con `bash tests/run_security_tests.sh`.
`tests/sandbox_probe.py <app> <WAV-sintético> [arm64|x86_64]` prepara una app de
prueba firmada, usa el controller de producción y el worker empaquetado, comprueba
EPERM en padre/hijo y recorre separación, escucha, exportación y cierre. No se
incluye esa sonda en la app entregada ni sustituye probar los selectores de GUI.

Para ejecutar el test de estado sin iniciar una app:

```sh
xcrun swiftc -swift-version 5 -module-cache-path build/swift-cache \
  src/JobState.swift tests/JobStateTests.swift -o build/job-state-tests
build/job-state-tests
```

Las pruebas, mediciones, límites y pendientes se registran en
`docs/validation.md`. Las evidencias crudas y los registros internos de
ejecución permanecen en el workspace local y están excluidos de Git. Este
proyecto no entrena ni recrea los pesos del modelo. Tampoco concede derechos
de redistribución sobre modelos o bibliotecas de terceros; sus dependencias
conservan sus propias licencias y avisos.

## Privacidad y seguridad

La app y su worker se firman con App Sandbox y sin permisos de red entrante ni
saliente. La telemetría del runtime se desactiva. No hay cuentas, servicios de
nube, descargador ni actualizador en la app. Las descargas de herramientas y
dependencias pertenecen exclusivamente a la preparación de desarrollo.

Cauces copia la entrada seleccionada a su área privada, sin modificar el
original. El worker usa esa copia: no hereda los permisos dinámicos del selector
de archivos. La GUI prepara, verifica por SHA-256 y publica los tres stems con
un rename exclusivo. Cancelar/cerrar detiene las copias en curso y limpia solo
los temporales cuya identidad sigue siendo la registrada. El repro de sustitución previa de la carpeta raíz conserva el contenido
sustituto. Las comprobaciones de identidad y unlink/rename no son atómicas:
un escritor concurrente del mismo usuario sigue fuera de la frontera de
aislamiento (puede competir sobre archivos internos o staging). Un cierre forzado del sistema
puede dejar temporales privados; no se promete borrado seguro de datos en SSD.

Se rechazan volúmenes no locales, archivos dataless y ubicaciones reconocidas de
iCloud, File Provider/CloudStorage, Dropbox, OneDrive, Google Drive y MEGA. **Elige una
carpeta que realmente no se sincronice:** Cauces no controla la configuración de
otras aplicaciones ni puede detectar todas las carpetas sincronizadas posibles.
El bloqueo de red de Cauces no bloquea servicios independientes de macOS.
El límite adicional de copia es 1 GiB por archivo.

La firma ad hoc habilita Hardened Runtime. El worker necesita la excepción de
library validation para cargar el runtime local ad hoc sin Team ID; no se
habilitan depuración, JIT, DYLD environment ni permisos de red. Esta excepción
limita la protección frente a sustitución de bibliotecas por otro proceso del
mismo usuario. La API C embebida por otra app depende del aislamiento de ese
proceso anfitrión; no se sandboxea por cargarla.

El nombre del modelo es una denominación de integración. La huella del
checkpoint base coincide con **MossFormer2_SS_16K, Alibaba Speech Lab**:
[ficha oficial del modelo](https://huggingface.co/alibabasglab/MossFormer2_SS_16K). La ficha identifica
Apache-2.0; no prueba equivalencia de todos los tensores convertidos ni derechos
sobre todos los assets.
Esta versión estima exactamente dos voces y un residual.

La conversión ONNX y el refinador fueron desarrollados por **GuerraMagica**, según
declaración del titular del proyecto del 02-11-2026. Esta atribución se incorpora
al aviso y al manifiesto del paquete 0.4.2; no modifica los tensores ni sustituye
las licencias de los componentes de terceros. Las referencias históricas a una
procedencia no identificada describen la información disponible en aquellas
auditorías, anterior a esta aclaración.

## Preparación comercial / Commercial preparation

El [dossier bilingüe de distribución](docs/commercial/README.md) reúne manual,
condiciones, privacidad, licencias, procedimientos de publicación y actas de
aceptación. Es documentación de preparación con decisiones pendientes; no
acredita que la beta esté autorizada para la venta ni modifica la app.

The [bilingual distribution dossier](docs/commercial/README.md) contains the user
guide, terms, privacy, licensing, release procedures and acceptance records. It is
a preparation pack with open decisions, not commercial clearance or an app change.
