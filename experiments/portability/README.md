# Cauces — experimento de portabilidad

Prueba del motor/CLI en Linux x64 y compilación cruzada Windows x64. No es una
versión de la aplicación para estas plataformas y no modifica el build macOS.
Los adaptadores son experimentales: no implementan el worker, sus temporales,
la exportación atómica, la GUI ni el aislamiento de producción.

Los [resultados del 05-11-2026](RESULTS.md) documentan nueve casos sintéticos
comparados con Mac. **Windows 11 no se ha ejecutado ni validado.**

Preparado con asistencia de IA (Codex), reutilizando el código de Cauces bajo
GPL-3.0-only. Se revisó y probó con los límites descritos en los resultados;
la asistencia de IA no acredita por sí misma corrección ni procedencia.

Este directorio publica scripts, adaptadores y el resumen de resultados.
Snapshots, dependencias, modelos, WAV, reportes crudos, ejecutables y kits
generados permanecen locales e ignorados. No se descargan modelos ni pesos.

## Preparar fuentes y dependencias

Ejecutar desde `experiments/portability/` con Git, Python 3.9+, curl y tar.
El snapshot queda fijado a la revisión usada en la prueba; debe estar disponible
en el historial local. Un clon con historial completo la incluye.

```sh
mkdir -p source deps
git -C ../.. archive 2aca032b34e1a8b899d4524e2b7b3b42a50cf397 -- src tests LICENSE | tar -x -C source
python3 prepare_source.py
python3 verify_probe.py generate
python3 verify_probe.py self-test

curl --fail --location --output deps/onnxruntime-linux-x64-1.31.1.tgz https://github.com/microsoft/onnxruntime/releases/download/v1.31.1/onnxruntime-linux-x64-1.31.1.tgz
curl --fail --location --output deps/onnxruntime-win-x64-1.31.1.zip https://github.com/microsoft/onnxruntime/releases/download/v1.31.1/onnxruntime-win-x64-1.31.1.zip
```

Antes de extraer, comprobar SHA-256 de los paquetes descargados. Son huellas
registradas en la ejecución local, no firmas independientes de upstream:

```text
c849e36a1ef3e22d4ff217b9d1ce4a3cf5b9467b975610913ae959ad5b16bdc9  onnxruntime-linux-x64-1.31.1.tgz
5869e26bb25314375f2d5ef1877e3ea06b1543d6c710e6e4a1ec2f7177ab4b2c  onnxruntime-win-x64-1.31.1.zip
```

```sh
tar -xzf deps/onnxruntime-linux-x64-1.31.1.tgz -C deps
python3 -m zipfile -e deps/onnxruntime-win-x64-1.31.1.zip deps
```

Los builds y pruebas sin inferencia no necesitan modelos. Para inferencia se
requiere una copia local autorizada de `separator.onnx`, `refiner.onnx` y
`weights.bin` con los hashes que fija Cauces. Su distribución no está cubierta
por publicar estos scripts; consultar [alcance de licencia](../../LICENSE_SCOPE.md).

## Compilar y comprobar Linux/Windows x64

Requiere Docker local. La construcción de la imagen instala herramientas de
desarrollo desde Ubuntu y usa red; no incorpora fuentes, audio ni modelos.

```sh
docker build --platform linux/amd64 -t cauces-portability-spike:20261104 .
```

Montar este directorio en `/work`; después de preparar dependencias se puede
compilar y ejecutar CTest sin red:

```sh
docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,src=$PWD,dst=/work" \
  cauces-portability-spike:20261104 sh build_linux.sh

docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,src=$PWD,dst=/work" \
  cauces-portability-spike:20261104 sh build_windows.sh
```

El segundo comando solo compila mediante MinGW. No ejecuta pruebas Windows.
En Apple Silicon, Linux x64 se ejecuta emulado: sus tiempos no son benchmarks
de un PC x64.

## Inferencia y comparación locales

Usar únicamente una carpeta de modelos autorizada y local, montada en solo
lectura. Sustituir el ejemplo por la ruta correspondiente:

```sh
docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,src=$PWD,dst=/work" \
  --mount "type=bind,src=/ruta/local/modelos,dst=/models,readonly" \
  cauces-portability-spike:20261104 \
  python3 verify_probe.py run build-linux-x64/pipeline_cli /models results/linux-x64
```

Cada destino de `run` debe ser nuevo; un fallo conserva su reporte. Para generar
una referencia con el motor Mac ya compilado del repositorio:

```sh
python3 verify_probe.py run ../../build/arm64/pipeline_cli ../../vendor/cauces-models results/mac-arm64
python3 verify_probe.py compare results/mac-arm64 results/linux-x64 results/comparison.json
```

El verificador comprueba muestras, canales, sample rate, BWF, float32, valores
finitos, suma de stems, rechazo de sobrescritura y del modelo alterado. Usa
`atol=1e-5` y `rtol=1e-4`; no interpreta diferencias numéricas como una evaluación
auditiva. Se niega a funcionar con `-O` o `PYTHONOPTIMIZE`.

## Preparar un kit Windows local

Con el build Windows, fixtures y referencia Mac anteriores ya disponibles:

```sh
docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,src=$PWD,dst=/work" \
  cauces-portability-spike:20261104 sh stage_windows.sh
```

Genera `windows-test-kit/` con ejecutables, DLL, avisos, scripts, fixtures y
referencia Mac. No incluye modelos. Rechaza un kit previo para preservar sus
archivos. Ver [WINDOWS.md](WINDOWS.md) para requisitos y ejecución futura.
El kit queda local; este repositorio no publica sus binarios ni sus audios.
