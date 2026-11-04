# Cauces 0.4.2 build 7 — candidato local

La referencia funcional es 0.4.2 build 6. Build 7 incorpora licencias, atribuciones,
información de dependencias y fuentes para distribución. Conserva modelos, DSP,
providers utilizados y permisos de App Sandbox. Los ZIP anteriores no se sustituyen.

El código, documentación y artwork propios se ofrecen bajo GPL-3.0-only. Los
modelos y bibliotecas conservan sus licencias y avisos. La declaración Apache-2.0
del separador se registra en su contexto; no se exige que incluya hashes para
ser una declaración válida. Los permisos del refinador continúan pendientes.
Por eso los artefactos completos se preparan localmente, sin publicar sus pesos.

## Dependencias y fuentes

- ARM64: paquete oficial ONNX Runtime 1.31.1, fuente identificada por el binario
  `41d4d61f14b9c1dd0b2ccda1e9b85dd415fd0496`.
- Intel: ONNX Runtime 1.31.1 compilado desde
  `6af1a932e2286d5c58166085d24c68783033edee`.
- JSON 3.11.3: árbol de headers y licencia raíz contrastados byte a byte con el
  origen fijado. Se conservan también las atribuciones adicionales de sus headers.

El [inventario](docs/release/dependency-inventory.json) distingue evidencia de
link/compilación Intel y pins upstream. ARM64 contiene CoreML, WebGPU y CPU;
Cauces utiliza CPU. El publicador no facilita SBOM por binario ni CMakeCache ARM64:
no se afirma conocer qué parte de cada dependencia está enlazada. Los avisos
originales completos se conservan como conjunto amplio. No se ha sustituido el
runtime para eliminar proveedores ni se promete reproducción binaria idéntica.

El archivo de fuentes propias se genera con `git archive` de un commit concreto,
sin vendor, pesos o evidencias privadas. La colección local de fuentes de terceros
contiene archivos upstream de ambas revisiones ORT y las dependencias CPU
verificadas por huella de árbol, con sus avisos
originales. Las dependencias de los proveedores ARM64 adicionales se identifican
mediante los pins y recetas upstream; la colección no se presenta como un SDK ARM64
completo que pueda reconstruir sin red el binario oficial.

## Compilar y probar

Requisitos y preparación del runtime: [README](README.md#compilar-y-verificar).
En un checkout nuevo, `bash scripts/prepare-runtime.sh` descarga dependencias
públicas fijadas y compila el runtime Intel; no obtiene los modelos de Cauces.

```sh
bash scripts/build.sh arm64 x86_64
bash tests/run_public_tests.sh all
# Integración local: requiere tus modelos y fixtures sintéticos autorizados.
bash tests/run_security_tests.sh all
# Crea dist/Cauces-0.4.2-build7/Cauces.app; rechaza sobrescribir una app existente.
bash scripts/package.sh
/usr/bin/python3 tests/package_test.py dist/Cauces-0.4.2-build7/Cauces.app
```

No copiar los fixtures privados al archivo público de fuentes. Para preparar las
fuentes externas ARM64 de este candidato:

```sh
curl --fail --location \
  https://codeload.github.com/microsoft/onnxruntime/tar.gz/41d4d61f14b9c1dd0b2ccda1e9b85dd415fd0496 \
  --output vendor/onnxruntime-arm64-src-1.31.1.tar.gz
printf '%s  %s\n' \
  2534907510879a8bfd9d11bae7c42a6632600960089b9f6cd2f6794404b9c111 \
  vendor/onnxruntime-arm64-src-1.31.1.tar.gz | shasum -a 256 -c -
tar -xzf vendor/onnxruntime-arm64-src-1.31.1.tar.gz -C vendor
/usr/bin/python3 scripts/audit_dependencies.py
```

El inventario contiene huellas de los runtimes revisados y de los árboles de
fuentes CPU. El empaquetador exige registros de compilación por arquitectura:
verifica insumos antes/después de compilar y los hashes de los binarios, y rechaza
fuentes, headers, dependencias o ejecutables cambiados desde aquella compilación. Si una compilación
local distinta cambia sus huellas, regenerar y revisar el inventario antes de
preparar la entrega; no copiar resultados de validación de otro binario.

## Preparar archivos de entrega

Con el árbol revisado, probado y comprometido en Git, elegir un destino nuevo:

```sh
/usr/bin/python3 scripts/prepare_release.py \
  --app "$PWD/dist/Cauces-0.4.2-build7/Cauces.app" \
  --output "$PWD/dist/Cauces-0.4.2-build7-delivery"
cd dist/Cauces-0.4.2-build7-delivery
shasum -a 256 -c SHA256SUMS
```

El manifiesto vincula commit, ZIP universal, fuentes propias y fuentes de terceros.
El candidato sigue firmado ad hoc y sin notarizar. Quedan pendientes escucha
profesional, Intel físico, Pro Tools, GUI manual y prueba pública de Gatekeeper.
Una transferencia local comprueba transporte e integridad, no esos comportamientos.
No se modifica la configuración de seguridad de macOS para aprobar una prueba.
