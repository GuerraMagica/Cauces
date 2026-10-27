# Separador de diálogo — beta personal 0.1

App local para macOS 15 o posterior, con ejecutables universales ARM64/Intel.
Separa dos voces y un residual utilizando los grafos y pesos locales de VoxUno
y una implementación propia del DSP. Interfaz SwiftUI; inferencia CPU con ONNX
Runtime 1.24.2; no requiere Python, cuentas ni conexiones durante el uso.

Este repositorio publica **código fuente, pruebas y documentación**. Los
modelos, pesos, audios, capturas del original, herramientas de investigación
y paquetes `.app`/ZIP no se distribuyen aquí. Los resultados documentados
proceden de la validación local; no equivalen a pruebas ejecutadas por GitHub.

## Uso

1. Abre `dist/Separador de diálogo.app` con doble clic.
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
sus modelos y runtime de cada arquitectura, por lo que no necesita VoxUno
instalado ni un entorno de desarrollo. Firma ad hoc local; no está notarizada
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
- `src/worker.cpp`: proceso persistente, integridad y exportación atómica.
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
`scripts/package.sh` acepta `MODEL_DIR` para indicar tu copia local autorizada;
por defecto utiliza la ubicación de instalación local de VoxUno. Los hashes
admitidos por el worker están fijados en `src/worker.cpp`.

Herramientas usadas en este equipo: Swift/Clang del SDK macOS 26.5, CMake y
Ninja existentes. Target de despliegue 15.0. No se instalaron herramientas
globales. Los modelos se copian desde su ubicación local; no se modifican.

El runtime ARM64 procede del paquete oficial 1.24.2. El runtime x86_64 se
compila desde `v1.24.2`, commit
`058787ceead760166e3c50a0a4cba8a833a6f53f`; configuración y hashes en
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
anterior antes de repetirlo. Las cinco suites CTest y `tests/JobStateTests.swift`
no necesitan modelos ni audios externos durante su ejecución. Los tests Python
de comparación, worker y paquete, y `WorkerConnectionTests.swift`, son pruebas
de integración local: necesitan los modelos, un Python con NumPy cuando
corresponda y el corpus de investigación hermano `voxuno-investigation/`, que
no se publica. Esos tests no forman parte de la app de destino ni se presentan
como reproducibles con este repositorio por sí solo.

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
