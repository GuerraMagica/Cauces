# Validación de la beta personal 0.1

27-10-2026. Pruebas locales en Apple M2, 16 GB, macOS 26.5.2. Objetivo de
despliegue macOS 15.0. Intel físico con Sequoia 15.7.5: **pendiente**.

Este documento resume una ejecución local previa a la publicación del código.
Las rutas `evidence/`, `build/` y `dist/` que aparecen abajo identifican
artefactos locales excluidos del repositorio público. No hay modelos, audios,
paquetes ni capturas originales publicados aquí, y no se afirma que GitHub
haya ejecutado las pruebas de inferencia.

## Resultado y artefactos

App universal ARM64/x86_64 en `dist/Separador de diálogo.app`, unos 247 MB;
ZIP personal de unos 177 MB y checksum en `dist/SHA256.txt`.
Firma ad hoc local comprobada, sin notarización Developer ID.
El paquete se descomprimió en `build/relocated-package/` y su worker procesó
audio no nulo en ambas arquitecturas (x86_64 bajo Rosetta), usando únicamente
el runtime y modelos contenidos en esa copia. No precisa Python en destino.

## Comparación con VoxUno CPU

Tolerancia fijada antes de implementar: `atol=1e-5`, `rtol=1e-4`. Se comprueban
también dimensiones, sample rate, finitud e integridad de cada entrada.

| Ejecución | Casos dentro de tolerancia | Casos bit a bit idénticos | Máximo error absoluto |
|---|---:|---:|---:|
| C++ ARM64, corpus original | 15/15 | 2/15 | 5.960464477539063e-08 |
| C++ x86_64 bajo Rosetta, mismo corpus | 15/15 | 2/15 | 3.516674041748047e-06 |
| C++ ARM64, mezcla sintética adicional de 30 s | 1/1 | No | 8.940696716308594e-08 |

ARM64 total: **16/16 (100%) dentro de tolerancia**; Intel/Rosetta: **15/15
(100%)**. No se afirma igualdad bit a bit general ni equivalencia GPU.
Las diferencias exactas de los otros 13 casos están conservadas, aunque
queden dentro de tolerancia.

Resultados y cada divergencia:

- `evidence/native-cpu-20261027-140034/results.json`: corpus ARM64 final.
- `evidence/native-cpu-x86_64-20261027-140155/results.json`: x86_64 final.
- `evidence/extended-30s/results.json`: mezcla de 30 s con múltiples bloques,
  solapamientos, alineación y ganancia global; capturas del VoxUno real.
- Cada carpeta contiene `divergences.csv`: **cero filas fuera de tolerancia**.
  `difference-manifest.json` y los NPZ por stem conservan todos los valores
  originales/nativos y todas las máscaras de diferencias IEEE754, además de
  las máscaras de tolerancia y hashes. El caso ampliado conserva sus NPZ.

El corpus cubre silencio, ceros con signo, impulso mínimo, límites 511/512/513,
8/16/44.1/48 kHz, dual mono y límites de bloques de refinado y separación.
Son fixtures sintéticos; no representan una validación de voces ni del acting.

## Rendimiento y recursos

| Entrada, motor ya cargado | Nuevo worker CPU | VoxUno CPU, interfaz real |
|---|---:|---:|
| 8 s | 18.29 s | 20.40 s |
| 30 s | 83.63 s | 91.23 s |

En estas mediciones queda por debajo del objetivo de no superar 2× VoxUno CPU.
Carga inicial del nuevo motor: 2.18 s en esa serie. Cuatro hilos por sesión,
ejecución secuencial, optimización ORT completa y spinning desactivado.
Prueba inicial aislada del modelo principal: ~55 s/8 s con un hilo frente a
~17 s con cuatro, tomada durante compilación; no se usa como benchmark final.

La nueva app mide dentro del worker; VoxUno se midió desde Open hasta la
primera observación de `3 stems ready`, con modelo precargado y observaciones
CUA repetidas. La captura de UI introduce overhead. Son comparaciones prácticas
con los mismos archivos sintéticos, no microbenchmarks ni garantías de velocidad.
Una primera observación de 30 s tenía un hueco de polling y se excluyó; se
repitió con seguimiento continuo. Mediciones crudas en `evidence/benchmark.json`
y `evidence/original-cpu-benchmark.json`.

La comparación numérica adicional de 30 s tardó 92.39 s con otros tests activos;
no sustituye la medición de rendimiento anterior ni se presenta como aislada.

Un WAV float32 mono de **30 minutos / 86.400.000 muestras** completó la ruta
de silencio y escritura con longitud intacta y hash/mtime del original iguales.
Pico RSS del proceso hijo durante la serie: **3.551.363.072 bytes (~3,31 GiB)**.
El caso largo de silencio omite la inferencia neuronal: no demuestra recursos
ni rendimiento sostenido de un diálogo no nulo de 30 minutos.

Los buffers grandes se preasignan en disco y se mapean, con eliminación del
nombre al abrirlos; los libera el sistema al cerrar/matar el proceso. Preflight
por máximos de buffers vivos, longitudes reales a 16/48 kHz y 512 MiB de reserva.
Ejemplos de 30 minutos mono: al menos 2.131.200.000 bytes de mapas a 8 kHz,
2.419.200.000 a 48 kHz, más reserva. Exportación comprueba aparte los tres WAV.
El límite de beta es 30 minutos; una prueba sostenida no nula de esa duración
y su aceptación auditiva siguen pendientes.

## Robustez e interfaz

- CTest: **5/5 grupos** en ARM64 y **5/5** en x86_64/Rosetta: DSP, pipeline,
  WAV/BWF, API C y límites de almacenamiento. Incluyen PCM24 con signo y
  extremos, PCM16/float32, crop/pad, FMA, STFT/iSTFT y muestras exactas.
- Worker real: nueve fixtures malformados/no admitidos; modelo ausente;
  comando desconocido; segundo trabajo tras error; colisión de exportación;
  hashes y mtime de origen; cierre normal y retirada de sus temporales.
- Transporte Swift real: cancelar inferencia, limpiar y reintentar; interrumpir
  exportación de un archivo temporal propio de 256 MiB y retirar staging al
  cerrar. La limpieza final es síncrona tras matar/esperar al worker.
- Máquina de estados: segundo trabajo, eventos antiguos, cancelación,
  recuperación y fallo de exportación sin perder el resultado válido, incluido
  un fallo local de creación de staging por permisos de destino. El transporte
  prueba una carpeta real sin permiso de escritura y permite reintentar después.
- UI observada: abrir mono y dual mono, separar, progreso, reproducción,
  cambiar pista en marcha, búsqueda mediante control accesible y exportar.
  El paquete final exportó y verificó dual mono desde su interfaz.
- Exportación float32 exclusiva, fsync y reapertura; BWF `time_reference`
  conservado, incluida una referencia de 64 bits en el test. Tres archivos
  preparados y verificados por hash antes de publicar la carpeta con rename
  exclusivo. Los directorios existentes, incluidos symlinks, se rechazan.
- Los nueve binarios/modelos originales conservan hash, tamaño y mtime:
  `evidence/original-assets-after-app.json`.

La revisión independiente detectó tres problemas importantes: carrera entre
cabecera y muestras, staging abandonado al cerrar y preflight insuficiente a
8 kHz. Los tres se corrigieron con regresiones; detalles en `progress.md`.

## Pendientes de aceptación

1. Ejecutar en el Mac Intel físico: apertura en Sequoia 15.7.5, separación,
   preescucha y exportación. Medir el objetivo Intel de 1 min de audio en ≤2 min;
   el resultado bajo Rosetta no permite predecirlo.
2. Escuchar diálogos representativos elegidos por el usuario, localmente;
   comprobar acting, respiración, solapamientos, artefactos y bleed frente a
   VoxUno. No se ha utilizado material de producción privado.
3. Verificar el round trip en Pro Tools y el BWF dentro de su flujo real.
4. Prueba sostenida con audio no nulo hasta 30 minutos y evaluación de CoreML.
   La beta funciona en CPU; no incluye aceleración GPU habilitada ni probada.

La app está implementada y probada localmente como beta personal. Estos
pendientes impiden declararla equivalente en calidad profesional o validada
en ambos equipos físicos.
