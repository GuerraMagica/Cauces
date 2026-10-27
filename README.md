# Cauces — beta personal 0.2

App local para macOS 15 o posterior, con ejecutables universales ARM64/Intel.
Separa dos voces y un residual con **Cauces Multi-Speaker Separation ONNX v1
(selective FP16)** y una implementación propia del DSP. Interfaz SwiftUI; inferencia CPU con ONNX
Runtime 1.31.1; no requiere Python, cuentas ni conexiones durante el uso.

Este repositorio publica **código fuente, pruebas y documentación**. Los
modelos, pesos, audios, capturas del original, herramientas de investigación
y paquetes `.app`/ZIP no se distribuyen aquí. Los resultados documentados
proceden de la validación local; no equivalen a pruebas ejecutadas por GitHub.

## Uso

1. Abre `dist/Cauces.app` con doble clic.
2. Abre o arrastra un WAV mono o dual mono idéntico: PCM16, PCM24 o float32,
   entre 8 y 48 kHz, hasta 30 minutos.
3. Pulsa **Separar voces**. Puedes cancelar; se descartan los resultados de ese
   trabajo y sus temporales. Solo se procesa un archivo a la vez.
4. Reproduce y cambia entre Original, Voz 1, Voz 2 y Residual. Las cuatro pistas
   comparten reloj y cursor; no hay normalización automática.
5. **Exportar tres stems…** crea `<nombre>_separado` en la carpeta que elijas.
   Contiene tres WAV float32 con mismo sample rate, muestras y canales. Una
   carpeta final existente provoca un error; no se sobrescribe.

Si el original tiene BWF, se conserva `time_reference` en muestras. No se
promete retención completa de iXML, UMID, historial, loudness o metadata
propietaria. El residual puede contener diálogo; las etiquetas de hablante son
estimaciones y pueden cambiar cuando la evidencia de solapamiento es débil.
No incluye estéreo real, batch, plugins de DAW ni procesamiento en tiempo real.

## Trasladarla al Intel

Copia la app completa o el ZIP personal, descomprímelo y abre la app. Incluye
sus modelos y runtime de cada arquitectura; no necesita otra aplicación
ni un entorno de desarrollo. Firma ad hoc local; no está notarizada
ni distribuida mediante Developer ID. No se han cambiado protecciones del
sistema. La apertura en el Intel físico debe comprobarse allí; Rosetta no
valida Sequoia ni su rendimiento.

Prueba primero una copia de un diálogo corto que puedas usar localmente:
abrir, separar, alternar pistas, buscar un punto, cancelar otro trabajo y
exportar. Reabre los tres stems en tu DAW para confirmar alineación y BWF.
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
