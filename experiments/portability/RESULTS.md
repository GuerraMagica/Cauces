# Cauces — resultado de la prueba de portabilidad

Fecha de cierre de la prueba: 05-11-2026. Alcance: motor/CLI, sin interfaz.
Base: snapshot del commit `2aca032` del repositorio local `dialogue-separator-app`.
Respaldo en GitHub autorizado posteriormente el 05-11-2026: scripts, adaptadores
y este resumen; sin modelos, audio, dependencias, binarios ni reportes crudos.

## Conclusión

La portabilidad del motor a Linux x64 queda demostrada para este corpus sintético.
Windows x64 compila y tiene un kit de prueba local, pero **no está validado en
Windows 11**: no se dispuso de equipo/VM Windows.
La fase queda parcialmente validada; no es una entrega de la aplicación completa.

Es viable compartir repositorio y motor entre macOS, Windows y Linux. Los
resultados respaldan conservar modelos y DSP, con adaptadores de plataforma.
No demuestran todavía viabilidad completa de GUI, reproducción o sandbox.

## Resultados comprobados

| Comprobación | Resultado |
|---|---|
| Contratos de referencia Mac ARM64, DSP/pipeline/WAV/API | 4/4 PASS |
| Contratos del build experimental Mac ARM64 | 4/4 PASS |
| Compilación y contratos Ubuntu 24.04 x64 | 4/4 PASS |
| ONNX Runtime Linux, separación y refinador | 1.31.1, dos recorridos de la sonda PASS |
| Separación/exportación Mac ARM64 | 9/9 casos, 27 WAV |
| Separación/exportación Mac x64 bajo Rosetta | 9/9 casos, 27 WAV |
| Separación/exportación Linux x64 emulado | 9/9 casos, 27 WAV |
| Canales, muestras, sample rate y BWF time_reference | Conservados en los 81 WAV |
| Sobrescritura de los resultados existentes | Rechazada en cada caso; archivos preservados |
| Copia del modelo con un byte alterado | Rechazada específicamente por hash en Mac/Linux |
| Compilación cruzada Windows x64 | PASS; ejecutable PE32+ x86-64 |
| Ejecución Windows 11, escucha y dispositivos | PENDIENTE; no se usó Windows ni Wine |

El corpus contiene señales matemáticas, sin voces ni material de producción:
PCM16, PCM24, float32; 8/16/44,1/48 kHz; mono y dual mono; silencio, cero con signo,
impulso, límites de bloque y 128001 muestras a 16 kHz (8,0000625 s). Incluye
time_reference ausente, cero y valores superiores a 32 bits.

## Comparación numérica

Tolerancias preexistentes, sin ampliarlas: `atol=1e-5`, `rtol=1e-4`.
Se comparó cada muestra de cada uno de los 27 stems de cada pareja.

| Referencia / candidato | Máximo error absoluto | Muestras fuera de tolerancia |
|---|---:|---:|
| Mac ARM64 / Linux x64 | 2,682209014892578e-6 | 0 |
| Mac x64 Rosetta / Linux x64 | 2,2649765014648438e-6 | 0 |
| Mac ARM64 / Mac x64 Rosetta | 3,7103891372680664e-6 | 0 |

Hay pequeñas diferencias numéricas: **no se afirma identidad bit a bit ni
equivalencia perceptiva**. El error máximo de reconstrucción de la suma de stems
respecto al original fue inferior a 2e-8 en los recorridos registrados.

Evidencia local, excluida de Git: `results/compare-*.json` y
`results/{mac-arm64,mac-x64-rosetta,linux-x64}/report.json` en el workspace
original del experimento. Estas rutas no son archivos publicados.
El SHA-256 del binario Linux usado en inferencia coincide con el build final:
`72b529a046a18da0f0ee70e09b90f3825d0c501d2cc8b072c52c94369cc83b41`.

## Implementación del experimento

- La prueba se ejecutó en un snapshot independiente; el motor y los paquetes
  de Cauces no se adaptaron. El respaldo añade únicamente este experimento.
- `prepare_source.py` genera adaptadores sin cambiar DSP/pipeline originales:
  OpenSSL para hash Linux, BCrypt para hash Windows, handles Win32 para WAV y
  modelos, y `ORT_TSTR` para la ruta de tensores externos de ONNX Runtime.
- MinGW requiere incluir explícitamente `cstdint`, inyectado por el build sin
  alterar las expresiones del DSP.
- CLI original `pipeline_cli`: almacenamiento en RAM. No es el worker de la app
  ni su exportación atómica mediante directorios privados.
- Los mismos tres assets mantienen sus hashes fijados. No se modificaron
  modelos, tensores, arquitectura, entrenamiento ni fórmulas numéricas.
- Docker ejecutó inferencia con `--network none` y modelos en bind mount
  `readonly`. Los assets no se incluyeron en el build de la imagen ni se subieron.

Entorno Linux: Ubuntu 24.04, glibc 2.39, GCC 13.3.0, CMake 3.28.3, x86-64
emulado sobre Apple Silicon. Imagen local:
`sha256:23fd3cbc7c69b9b56700bb81ed79ec4940405e6736e899942f23f21f4a54b6cd`.
La emulación, el uso de un hilo y la carga concurrente impiden inferir rendimiento
de un PC Linux/Windows. Los tiempos del log no son benchmarks comparables.

Los paquetes ONNX Runtime se descargaron de los assets oficiales de la versión
1.31.1. Sus hashes locales están en `results/dependency-hashes.json`; registrarlos
no equivale a una verificación independiente de firma upstream.

## Validación del verificador y revisión

El verificador independiente de RIFF usa únicamente Python estándar. Sus
controles detectan metadata, longitud, formato, NaN, audio y divergencia numérica
alterados. Se comprobó el rechazo de `-O` y `PYTHONOPTIMIZE` para evitar que se
desactiven sus assertions. El staging del kit se niega a sobrescribir un kit
previo; se comprobó que conserva sus 54 archivos de payload.

Una revisión independiente parcial encontró estos dos defectos del tooling,
corregidos y verificados. El revisor no pudo completar su dictamen por límite
de uso. La revisión final restante fue del propio implementador; no se afirma
una revisión independiente completa ni aptitud de estos adaptadores para producción.

Original preservado: hashes de los 218 archivos versionados y de los tres assets
comprobados; mismo commit y Git limpio. Evidencia: `results/original-preserved.json`.
El respaldo autorizado posterior añade scripts y documentación a
`experiments/portability/`, sin integrarlos en los targets de la aplicación.
Antes de ese respaldo se repitieron las pruebas públicas macOS ARM64 y
x86_64/Rosetta: 8/8 CTest y cinco suites Swift por arquitectura, protocolo y
WAV malformados, PASS. Desde la ubicación versionable se repitieron el build
Linux (4/4 contratos), la compilación cruzada Windows y las comparaciones con
los resultados locales. Dockerfile corregido para seleccionar la arquitectura
en la línea de comandos; `docker build --check` termina sin advertencias.

## Reproducción y kit Windows

La [guía de reproducción](README.md) describe cómo generar el snapshot fijado,
obtener dependencias y ejecutar las pruebas. Los scripts `build_linux.sh` y
`build_windows.sh` usan el contenedor de desarrollo local y los runtimes de
`deps/`. Ejecutarlos con este directorio montado en `/work`.

La inferencia Linux usada fue:

```sh
python3 verify_probe.py run build-linux-x64/pipeline_cli /models results/linux-x64
```

El destino debe ser nuevo. `/models` debe apuntar a una copia local autorizada
montada en solo lectura; deshabilitar la red del contenedor durante la prueba.
Para comparar los resultados ya guardados, sin repetir inferencia:

```sh
python3 verify_probe.py compare results/mac-arm64 results/linux-x64 results/compare-mac-arm64-linux-x64.json
```

El kit local `windows-test-kit/` contiene ejecutables, DLL, avisos, verificador, fixtures y
referencia Mac; no contiene pesos/modelos. Ver `windows-test-kit/WINDOWS.md` y
`Run-Probe.ps1`. `SHA256.json` registra sus 54 archivos de payload. La inspección
de imports confirma dependencia del runtime Microsoft Visual C++ x64 además de
DLL incluidas y componentes del sistema; **no se ha probado que carguen en Windows**.

## Pendientes y siguiente decisión

1. Ejecutar el kit en Windows 11 x64 con assets locales autorizados.
2. Antes de integrar: adaptar y probar worker, temporales, permisos, limpieza,
   publicación de exportaciones y aislamiento sin red de cada sistema.
3. Diseñar la interfaz Windows/Linux y su reproducción sincronizada; comprobar
   salidas reales y el comportamiento al cambiar/desconectar dispositivos.
4. Paquetes por sistema/arquitectura, compatibilidad Linux declarada y pruebas
   de proyectos largos; escucha profesional y verificación en DAW por separado.

Se mantiene como estimación preliminar el rango de 11–20 jornadas para una beta
Windows/Linux x64, condicionado a disponer de entornos reales y resolver los
pendientes anteriores. El spike reduce incertidumbre del motor Linux; no elimina
el trabajo de interfaz, audio, seguridad y distribución. No se ha iniciado esa fase.
