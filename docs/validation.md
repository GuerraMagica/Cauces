# Validación de Cauces

## Preparación técnica 0.4.2 build 7 — 04-11-2026

- Referencia funcional: 0.4.2 build 6, conservada con su ZIP original. Build 7
  cambia únicamente infraestructura de distribución y número de build; no cambia
  `src/`, pesos, modelos, runtime de cada arquitectura ni entitlements.
- Build C++/Swift ARM64 y x86_64 desde un snapshot nuevo de fuentes, sin modelos
  ni capturas privadas. Solo se copiaron dependencias de desarrollo fijadas.
  Las fuentes no enlazan con el checkout original. Compilación PASS.
- Pruebas públicas definitivas: 8/8 CTest por arquitectura, cinco suites Swift por
  arquitectura, protocolo/FIFO y 100 WAV malformados más recuperación: PASS.
  Contratos del runner (7), informes CTest (6), licencias (3), registros de build
  (4) y fuentes de terceros (3): PASS. Se observaron fallos antes de implementar
  los controles nuevos y el tratamiento de enlaces legítimos internos de upstream.
- Integración local ARM64/x86_64: transporte, cancelación/reintento, 18 rechazos
  individuales de assets por arquitectura, controles válidos y worker/exportación
  PASS. Solo fixtures sintéticos autorizados; originales preservados.
- Tras añadir los registros por arquitectura se recompilaron ambos recorridos;
  los seis ejecutables/bibliotecas de entrega resultantes coinciden byte a byte
  con los ya probados. Los registros verifican insumos antes/después del build,
  outputs y huellas ORT revisadas antes de empaquetar. Rechazo de empaquetado sobre
  una app existente comprobado sin modificar ninguno de sus archivos.
- Bundle universal build 7: firma ad hoc, dependencias relativas, mínimo macOS 15,
  hashes de modelos y 31 archivos de licencias/avisos comprobados. GPL, alcance,
  Apache, originales ORT y atribuciones JSON/CPU adicionales incluidos. Las huellas
  de sus 71 insumos de fuentes/licencias se contrastan al preparar la entrega.
- Sondas del controller de producción con worker empaquetado en ambas
  arquitecturas PASS: red EPERM en padre/hijo, inspect, separación, playback,
  exportación de tres stems, cancelación y cierre. Export sintético: 48000 Hz,
  2400 frames. El entry point de GUI se sustituye solo en una copia de prueba;
  no se presenta como aceptación manual del selector o escucha profesional.
- Revisión independiente: corregidos dos P2 de vinculación fuente/binario y
  validación de fuentes externas; segunda revisión sin hallazgos importantes.
  Los 12 árboles CPU y sus 20 avisos adicionales quedan registrados y verificados.
- El binario ARM64 oficial identifica un commit distinto del Intel local. Se han
  obtenido sus fuentes exactas; pins y avisos completos están inventariados. No
  se dispone de un SBOM oficial que certifique inclusión exacta por componente
  ARM64; los pins upstream se documentan como conjunto amplio, no como prueba de
  enlace. No se ha sustituido el runtime para eliminar esta limitación.
- Archivos de entrega generados desde `605cc73`: checksums de ZIP, fuentes y
  manifiesto PASS. Archivo de fuentes propias y descarga pública desde GitHub:
  218 archivos idénticos al commit. Fuentes externas entregadas: archivo upstream
  ARM64 exacto, git archive del commit Intel y 12 árboles CPU contrastados por
  contenido y enlaces internos. Transferencia HTTP local y extracción del ZIP:
  49 archivos del bundle idénticos; controles del paquete trasladado PASS.
- Evidencia local excluida de Git: `evidence/release-preparation-20261104/`.
  Artefactos locales y procedimiento de fuentes/descarga: [RELEASE.md](../RELEASE.md).
  Quedan pendientes permisos de modelos, escucha, Intel físico, Pro Tools, GUI
  manual y aceptación de Gatekeeper desde Internet. No se ha notarizado la app.

## Corrección de procedencia y metadatos — 04-11-2026

- README, aviso fuente e inventario dejan de atribuir como autoría acreditada la
  conversión ONNX y el refinador al titular. Se registra la coincidencia SHA-256
  con una distribución local de terceros y su declaración Apache-2.0 para el
  modelo de banda baja. El alcance sobre aportaciones específicas del exportador
  y los permisos del refinador siguen pendientes; ver
  [procedencia](commercial/LICENSES_PROVENANCE.md).
- `scripts/model_manifest.py` genera autores desconocidos como `null`, separa la
  licencia base del estado del refinador y conserva ONNX v1 como etiqueta local.
  Prueba temporal ejecutada sobre un manifiesto sintético: rechazo observado con
  el generador anterior; PASS tras la corrección. Comprueba ámbitos de licencia,
  preservación de campos fuera de `name`/`integration` e idempotencia.
- Ejecución adicional sobre una copia temporal del manifiesto real: todos los
  campos ajenos a `name`/`integration` se conservan. El original no se modifica.
  JSON del inventario, hashes de avisos históricos/actuales y enlaces locales
  modificados comprobados. `git diff --check` sin errores.
- Comparación SHA-256 de 43 archivos protegidos: modelos, manifiesto original,
  fuentes de procesamiento, licencias originales, entitlements, CMake,
  empaquetador y ZIP 0.4.2 permanecen intactos. No se ha compilado ni empaquetado
  una app nueva, ejecutado inferencia o repetido la escucha/suite de audio por
  estos cambios documentales y de metadatos.

## Pruebas públicas reproducibles — 04-11-2026

- Nuevo `tests/run_public_tests.sh [arm64|x86_64|all]`, con arquitectura actual
  por defecto. Separa CTest, cinco suites Swift independientes y WAV/protocolo
  sintéticos de la integración que necesita assets privados. No modifica código
  de producción, modelos, DSP, entitlements ni paquetes existentes.
- `run_integration_tests.sh` conserva transporte, cancelación/reintento, rechazo
  individual de assets y worker/exportación. `run_security_tests.sh` sigue
  ejecutando públicas e integración, ambas arquitecturas por defecto. Las pruebas
  de worker y WAV verifican ahora la arquitectura pedida; WAV tiene timeout y
  recuperación explícita con una entrada válida tras 100 casos malformados.
- TDD: siete contratos de CLI/preflight y seis de informes CTest pasan. Se
  observaron fallos antes de implementar los recorridos y el rechazo de informes
  incompletos. Ayuda, argumentos inválidos y requisitos ausentes no lanzan pruebas
  ni crean builds. No se confunde una integración sin assets con una suite pasada.
- Copia de fuentes limpia basada en `a15775d`, con los cambios de pruebas bajo
  revisión. Solo se copiaron dependencias de desarrollo permitidas: headers y
  bibliotecas ORT/JSON; sin modelos, WAV privados, capturas CPU ni enlaces al
  workspace original. Se conservaron únicamente enlaces relativos internos del
  runtime. Build C++ y GUI ARM64/x86_64 PASS, sin descargar ni instalar herramientas.
- `bash tests/run_public_tests.sh all` en esa copia: 8/8 CTest por arquitectura,
  5/5 suites Swift por arquitectura, protocolo/FIFO y 100 WAV malformados más
  recuperación por arquitectura PASS. Variables de modelos/fixtures apuntaban
  deliberadamente a destinos inexistentes. El recorrido no las necesita.
- `bash tests/run_security_tests.sh all` con los assets sintéticos locales:
  públicas e integración PASS en ambas arquitecturas. Transporte real, 18 rechazos
  individuales por arquitectura (36 en total), controles válidos y exportación
  pasan. Los originales se verifican sin cambios por SHA-256; no se usa audio de
  producción. x86_64 se ejecuta bajo Rosetta, no en Intel físico.
- Revisión independiente: se detectó que un registro CTest parcial podía aparentar
  éxito. Se añadió un validador que exige los ocho contratos publicados y rechaza
  skipped/failure/error, manteniendo la posibilidad de añadir más pruebas. Repro
  real en un build temporal sin `wav_without_dev_fd`: siete CTests pasan, pero el
  runner devuelve error y no anuncia PASS. Se restauró el registro y se repitieron
  públicas e integración con éxito. La corrección tiene seis contratos específicos.
- Primer intento de la copia limpia: dos CTests fallaron porque la preparación
  había omitido `libonnxruntime.1.dylib`, enlace interno requerido por dyld. Se
  completó la copia del runtime y se verificó el loader en ambas arquitecturas;
  no se cambió CMake ni código de producción. Se conserva el log fallido.
- La prueba `/dev/fd` se ejecutó con permiso para crear su política temporal de
  macOS. No se desactivaron protecciones ni se omitieron pruebas. Las suites de
  salida usan hardware simulado; no se cambió el reloj de una interfaz real.
- Evidencia cruda local, excluida de Git: `evidence/public-tests-20261104/`.
  README y CONTRIBUTING describen requisitos, comandos y separación de categorías.
  No se han verificado aquí descargas de dependencias desde cero, GUI empaquetada,
  App Sandbox real, Intel físico, escucha profesional ni Pro Tools. Los derechos
  pendientes de modelos y la distribución de la app completa siguen pendientes.

## Cauces 0.4.2 — Paquete actualizado (02-11-2026)

- Bundle universal nuevo, build 6, sin sobrescribir las versiones anteriores.
  Aviso y manifiesto históricos atribuyen conversión ONNX y refinador a GuerraMagica
  según declaración del titular del proyecto del 02-11-2026; se conserva la atribución
  del modelo base y las obligaciones de componentes de terceros. La declaración
  de autoría no se presenta como una comprobación jurídica independiente y queda
  corregida en las fuentes actuales por la revisión del 04-11-2026, arriba.
- Modelos, pesos, biblioteca numérica, ONNX Runtime y worker son byte a byte
  idénticos a 0.4.1. El manifiesto solo cambia la información de integración;
  todos los demás campos se conservan. No se modifica código DSP ni inferencia.
- Build ARM64/x86_64 y suite completa PASS: 8/8 CTest por arquitectura, transporte
  Swift/protocolo en ambas, 36 rechazos individuales de assets y controles válidos,
  100 WAV malformados y exportación. No se instala ni descarga ninguna dependencia.
- Paquete firmado ad hoc con App Sandbox y sin permisos de red. Probes del
  controller/worker pasan en ARM64 y x86_64/Rosetta: separación, playback,
  exportación, cancelación y cierre; conexión EPERM en padre/hijo, WAV exportados
  a 44100 Hz con 352800 muestras. El probe sustituye el entry point de una copia;
  no prueba aquí la selección manual de archivos ni escucha profesional.
- ZIP extraído fuera del repositorio: 19 archivos comparados por SHA-256 con el
  bundle; pruebas de arquitectura, firma, dependencias y modelos PASS.
- Artefactos locales: `dist/Cauces-0.4.2-universal.zip` (190627861 bytes) y
  `dist/Cauces-0.4.2-SHA256.txt`. SHA-256 del ZIP:
  `c0475f568066646582c9857c9fc91643048947f003c0b6d9782bb52bdf0c6d6c`.
  Evidencia: `evidence/cauces-release-0.4.2/`.
- Siguen pendientes Intel físico/Sequoia, diferencia perceptiva del reproductor,
  escucha de acting y round trip Pro Tools. Esta entrega no mejora ni cambia la
  separación. Firma sin notarización; modelos y ZIP permanecen fuera de GitHub.

## Regresiones de infraestructura — 01-11-2026

- Cambios limitados a pruebas, documentación e instrucciones de Git. El código
  de producción, modelos, pesos, DSP, runtime y paquete 0.4.1 quedan intactos.
- `tests/run_security_tests.sh`: 8/8 CTest ARM64 y 8/8 x86_64/Rosetta; contratos
  Swift, 100 WAV malformados y protocolo/exportación existentes pasan.
- Protocolo en ambas arquitecturas: seis payloads adversariales, cinco argumentos
  de threads inválidos y FIFO como entrada tanto de `inspect` como de `separate`
  (hash del origen). Se exige error acotado y recuperación con un WAV válido.
- Integridad en ambas arquitecturas: cada uno de separator.onnx, refiner.onnx y
  weights.bin se altera, elimina o sustituye por FIFO individualmente en un clon
  privado, con los otros assets válidos. Worker y API C rechazan los nueve casos:
  36 rechazos comprobados entre ambos entry points y ambas arquitecturas.
  Controles positivos antes/después aceptan los assets aprobados. Hash, tamaño y
  mtime de los originales se conservan. Los probes de API tienen timeout externo
  y verifican su arquitectura real; no se carga una dylib x86_64 desde Python ARM.
- Transporte Swift compilado para cada arquitectura contra su worker real:
  progreso antes de cancelar, limpieza sincronizada y reintento pasan.
- Paquete 0.4.1 y ZIP extraído fuera del proyecto: firma, arquitecturas, rutas
  relativas, entitlements y hashes pasan. Probes del controller/worker del bundle
  en ARM64/x86_64 pasan inspección, separación, playback, exportación, cancelación
  y cierre; red denegada con EPERM en padre/hijo. Exports conservan 44100 Hz y
  352800 muestras. No se modifican dispositivos ni preferencias de reproducción.
- Evidencia local ignorada: `evidence/security-regressions-20261101/`.
  Las pruebas de paquete/sandbox se ejecutan por separado de la suite general.
- Sin cambios trasladados del LAB ni nueva afirmación de calidad. Los 30/30 casos
  de la auditoría del 28-10 son históricos; no se repiten como parte de este
  refuerzo. Siguen pendientes la diferencia perceptiva del reproductor, escucha
  de diálogo real/acting, Intel físico, Pro Tools y metadata ajena al contrato
  BWF time_reference ya probado.

## Cauces 0.4.1 — Portabilidad del lector WAV (2026-10-28)

- Error fotografiado reproducido con un WAV sintético válido al denegar la
  reapertura de `/dev/fd`. El lector anterior falla; el lector nuevo pasa la
  misma prueba. Esto identifica una causa reproducible compatible con el síntoma;
  la causa efectiva en el equipo remoto requiere su nueva prueba.
- `src/wav.cpp` conserva el descriptor abierto y verificado y lee con `pread`:
  RAII, reintento de EINTR, lecturas cortas, EOF/truncación y offsets acotados.
  Conserva O_NOFOLLOW/O_NONBLOCK/O_CLOEXEC, comprobación de archivo regular,
  parser y conversiones. No se amplían permisos ni dependencias.
- `tests/run_security_tests.sh`: 8/8 grupos CTest por arquitectura ARM64 y
  x86_64/Rosetta, incluido control explícito de denegación de `/dev/fd`;
  contratos Swift, protocolo, integridad, 100 WAV malformados y exportación pasan.
  Casos añadidos: extremos PCM16, truncación tras header y cierre de descriptores
  en errores repetidos. Revisión independiente sin bloqueantes materiales.
- Probes del controller de producción y worker del ZIP extraído pasan en ambas
  arquitecturas con App Sandbox: inspección, separación, reproducción, exportación,
  cancelación y cierre. Tres WAV conservan 44100 Hz y 352800 muestras;
  conexión de control denegada con EPERM en padre/hijo.
- Intento adicional de combinar sandbox-exec con el App Sandbox del controller:
  libsecinit aborta antes del entry point en ambas arquitecturas. No se cuenta
  como prueba funcional. Se verifican por separado App Sandbox y lector bajo
  denegación de `/dev/fd`; no se afirma haber combinado esas dos políticas.
- GUI real del ZIP extraído: abre el fixture sintético PCM16/44100 Hz y termina
  la separación; controles de reproducción y Export audio disponibles.
- ZIP extraído fuera del repositorio: 19 archivos con hashes idénticos al bundle,
  firmas, arquitecturas y rutas relativas verificados. Modelos, runtime ONNX,
  biblioteca numérica e icono son byte a byte idénticos a 0.4.0.
- Evidencia local: `evidence/cauces-portability-0.4.1/`. Distribución personal:
  `dist/Cauces-0.4.1-universal.zip` y `dist/Cauces-0.4.1-SHA256.txt`.
  Subida TLS verificada en el destino autorizado `/SONIDO`: ZIP de 190627808
  bytes y checksum de 93 bytes, listado remoto presente y cola vacía.
  Se preservan los paquetes anteriores. Sin commit/push.
- Pendiente: prueba del mismo WAV en el Xeon W físico/Sequoia 15.7.5 y aceptación
  auditiva profesional. La firma ad hoc sigue sin notarización.


## Cauces 0.4.0 — Output Settings (2026-10-28)

- Ventana nativa Settings por menú/⌘,: Output, System Default, Sample rate,
  Device default, Apply/Cancel; paleta Flow. Persistencia por UID y frecuencia
  solicitada; reloj escrito solo en Apply. Sin dependencias/entitlements nuevos.
- Modelo probado con hardware simulado en ARM64 y x86_64: UID/default, persistencia,
  NaN/Inf/frecuencias no admitidas, ausencia de dispositivo, negativa del driver,
  fallo de routing después de escribir el clock, rollback, cambios externos,
  desconexión, fallo de consulta sin usar caché antigua y bloqueo de Play en Apply.
  Device default sigue una frecuencia cambiada externamente sin escribirla.
- Core Audio registra un listener del destino antes de solicitar la frecuencia y
  espera su confirmación. Apply verifica estabilidad y disponibilidad al finalizar;
  solo entonces guarda las preferencias. Las notificaciones del engine llevan
  generación y se procesan en main sin tareas antiguas sobre el graph nuevo.
- Probes con sources de producción dentro de bundles firmados/sandboxed, ARM64 y
  x86_64/Rosetta: Audio Bridge 2-A aplica **44100 Hz**, reproduce el fixture48kHz,
  conserva duración/cursor/pista2, Apply pausa y vuelve a **48000 Hz**. Las dos
  pruebas estrictas pasan sin permitir rechazo. Se restaura la frecuencia inicial.
- Altavoces integrados: fixture44.1kHz reproducido a48kHz con transporte correcto;
  la petición44.1kHz se revierte a48kHz. Un control sin AVAudioEngine y otro sin
  App Sandbox reproducen la reversión: la causa externa/driver/clock permanece
  desconocida. No se atribuye ese resultado al motor ni a las protecciones.
  Se verifica rechazo sin persistir y rollback. No se cerraron otras apps ni se
  relajó el sandbox para conseguir un resultado positivo.
- Controller de producción + worker final: inspección, separación, playback,
  exportación3WAV, cancelación y cierre pasan en ambos targets. Exports conservan
  **44100 Hz y352800muestras** con hardware48kHz; conexión de control denegada
  **EPERM** en padre/hijo. Los probes sustituyen el entry point GUI de una copia
  de prueba y no se distribuyen dentro de Cauces.
- Suites existentes `tests/run_security_tests.sh`: pasan7gruposCTest por target,
  contratos Swift, transporte,100WAVmalformados, integridad y protocolo/exportación.
  Revisión independiente: corregidos bloqueo duranteApply, callbacks antiguos,
  confirmación post-routing y semántica Device default; sin bloqueantes finales.
- GUI real: ⌘, abre Settings antes de importar; menú de dispositivos/frecuencias;
  Cancel no guarda; Apply a44100 en Audio Bridge funciona; reiniciar conserva UID,
  frecuencia y valor actual44100. Se restaura Audio Bridge48000 y System Default /
  Device default al terminar las pruebas.
- Evidencia local: `evidence/cauces-settings-0.4/`. ZIP0.4universal, firma/entitlements,
  extracción/hashes y modelos comparados con0.3.0. Source C++ intacto desde0.3.0.
- Pendientes: Intel físico/Sequoia15.7.5, desconexión física de interfaz externa,
  otros drivers/clock externo/frecuencias y escucha profesional/roundtrip ProTools.
  La app conserva firma ad hoc sin notarización. Ningún nuevo commit/push.


## Cauces 0.3.0 — Flow UI (2026-10-28)

- Interfaz SwiftUI nativa en inglés, artwork Flow, selección con check visible,
  exportación denominada **Export audio…**, firma **© GuerraMagica Audio** e
  icono ICNS real incluido en el bundle. Atajos ⌘O, Return, Escape, ⌘1–⌘4 y Espacio.
- `scripts/build.sh`: compilación ARM64 y x86_64 con deployment target 15.0.
  `tests/run_security_tests.sh`: todas las comprobaciones pasan: 7 grupos CTest
  por arquitectura, estados/copia/transporte Swift, diagnóstico inglés, protocolo,
  integridad de modelos y 100 WAV malformados reproducibles.
- Pruebas del controller de producción y worker empaquetado en ambas arquitecturas
  (Intel bajo Rosetta): separación, playback, tres exportaciones, cancelación y
  cierre correctos. App Sandbox deniega la conexión TCP de control en padre e hijo
  con `EPERM`. El ejecutable del probe sustituye la entrada GUI; no sustituye la
  comprobación adicional de importación/exportación mediante paneles nativos.
- UI real observada: abrir fixture sintético, progreso, alternar pista, reproducir/
  pausar, seek accesible confirmado por cambio de posición, exportar tres WAV,
  cancelación con Escape, error de RIFF en inglés y nombre largo en ventana mínima.
- Paquete universal verificado: firma ad hoc/Hardened Runtime, sandbox sin permisos
  de red, dos arquitecturas, dylibs relativas, modelos, artwork e icono. Los hashes
  de todos los modelos coinciden con 0.2.0. Los nueve .cpp modificados son idénticos
  a la base fuera de los literales de texto. Esta revisión no añade una nueva
  afirmación de equivalencia numérica ni de mejora en calidad de audio.
- Evidencia local: `evidence/cauces-ui-0.3/`; pruebas de preservación en
  `preservation.json`, resultados de sandbox separados por arquitectura y capturas
  nativas. Los primeros probes abortaron dentro del sandbox de Codex; se repitieron
  fuera de ese límite para probar el App Sandbox propio del bundle y pasaron.
- ZIP personal: `dist/Cauces-0.3.0-universal.zip`. Conserva la app/ZIP 0.2.0.
  Pendientes: Mac Intel físico con Sequoia 15.7.5, aceptación auditiva profesional
  y round trip en Pro Tools. La firma sigue siendo ad hoc; no está notarizada.


27–28-10-2026. Pruebas locales en Apple M2, 16 GB, macOS 26.5.2. Objetivo de
despliegue macOS 15.0. Intel físico con Sequoia 15.7.5: **pendiente**.

Las secciones históricas describen la beta 0.1 y no deben atribuirse al paquete
0.2 ni al runtime actualizado.
Las rutas `evidence/`, `build/` y `dist/` que aparecen abajo identifican
artefactos locales excluidos del repositorio público. No hay modelos, audios,
paquetes ni capturas originales publicados aquí, y no se afirma que GitHub
haya ejecutado las pruebas de inferencia.

## Cauces 0.2: seguridad y runtime 1.31.1

Nombre de integración: **Cauces Multi-Speaker Separation ONNX v1 (selective FP16)**.
Los cuatro assets binarios conservan sus SHA-256; solo cambia el manifiesto de
la copia propia. El código de la rama local de seguridad se valida con datos
sintéticos. No se han publicado modelos, audios ni un paquete nuevo en GitHub.

| Runtime 1.31.1 CPU | Casos dentro de tolerancia | Casos bit a bit | Máximo error absoluto |
|---|---:|---:|---:|
| ARM64, corpus de 15 casos | 15/15 | 2/15 | 3.069639205932617e-06 |
| x86_64/Rosetta, mismo corpus | 15/15 | 2/15 | 4.455447196960449e-06 |
| ARM64, mezcla adicional de 30 s | 1/1 | 0/1 | 1.5310943126678467e-06 |

Se conservan `atol=1e-5`, `rtol=1e-4`: **31/31 comparaciones dentro de tolerancia**.
Esto no implica igualdad bit a bit ni aceptación auditiva profesional.
CSV de divergencias fuera de tolerancia: cero filas. Valores originales/nativos,
máscaras de diferencias IEEE754 y hashes se conservan en NPZ y manifests:

- `evidence/native-cpu-arm64-20261027-233543/`.
- `evidence/native-cpu-x86_64-20261027-234951/`.
- `evidence/runtime-1.31.1-30s-arm64/`.

Seguridad y robustez comprobadas:

- Siete grupos CTest pasan en ambas arquitecturas: DSP, pipeline, WAV/BWF, API C,
  limpieza por identidad, límites de almacenamiento y rechazo de FIFO.
- Seis comandos JSON malformados/adversariales, cinco argumentos de hilos
  inválidos y 100 WAV malformados se rechazan sin crash; el protocolo recupera.
- El JSON de profundidad 50.000 antes provocaba SIGSEGV; ahora devuelve un error
  acotado. Las líneas se limitan antes de acumularlas y los ids son enteros.
- Reproducciones C++ y Swift de raíz temporal movida/reutilizada conservan el
  contenido sustituto. La limpieza recorre descriptores anclados y no sigue
  symlinks; copia y publicación usan creación/rename exclusivos.
- Copias con SHA-256, cancelación, colisiones, rutas inválidas y origen FIFO;
  cancelación/reintento con worker real y limpieza síncrona; estado de GUI.
- La API C rechaza archivos de modelos ajenos al conjunto permitido antes de
  entregarlos al runtime. Se cargan grafos y pesos desde los mismos buffers
  verificados; no se reabren rutas entre verificación y sesiones.
- App Sandbox sin permisos de red, Hardened Runtime y firma ad hoc verificados
  en el paquete universal. Sondas de test con el controller real y cada slice
  del worker comprueban EPERM en padre/hijo, inspección, separación no nula,
  reproducción, exportación de tres stems, cancelación y cierre. Las sondas no
  se incluyen en el paquete entregado.
- GUI real: NSOpenPanel, copia local privada, separación de 8 s, reproducción,
  cambio de pista, búsqueda accesible y exportación a un destino concedido por
  el usuario funcionan. Hash, tamaño y mtime de la entrada conservados durante
  separación/exportación. Una carpeta sintética local llamada MEGA verifica el
  rechazo de la política sin acceder a un proveedor de nube real.

La copia de desarrollo oficial del runtime ARM64 se verificó contra el SHA-256
publicado por GitHub; Intel se compiló desde el commit fijado
`6af1a932e2286d5c58166085d24c68783033edee`. La fuente contiene el endurecimiento
posterior al runtime anterior; no se afirma una auditoría exhaustiva de todos
sus componentes. Telemetría desactivada, proveedor CPU.

**Límites de seguridad:** se deniega la red de los procesos de Cauces; no se
controlan servicios de macOS u otras apps sincronizadoras. La política rechaza
volúmenes no locales, dataless y raíces de nube reconocidas; no descubre todas
las configuraciones de sincronización posibles. No se probó un volumen SMB
real ni un proveedor de nube con audio: se evita generar tráfico de prueba a
esos servicios. Las comprobaciones de identidad y unlink/rename no son atómicas
frente a escritores concurrentes del mismo usuario. El repro de la raíz
sustituida queda resuelto; un proceso hostil con acceso de escritura sigue fuera
de la frontera de aislamiento. La firma ad hoc requiere desactivar library
validation solo en el worker para cargar la biblioteca local sin Team ID;
no hay permisos de JIT, depuración ni variables DYLD. No hay notarización.

La documentación actual y los scripts propios ya no dependen de la marca o de
la instalación anterior. Se conserva la atribución a MossFormer2 y la
procedencia no identificada del refiner; el nombre Cauces no implica haber
entrenado los pesos ni derechos de redistribución sobre todos los assets.
Las capturas y evidencias históricas originales permanecen intactas.

Resultados detallados y logs: `evidence/security-audit-20261027/`. Los tiempos de
las pruebas nuevas se tomaron junto a compilación/otras pruebas; no son una
comparativa aislada de rendimiento. No se ha repetido una prueba neural no
silenciosa de 30 minutos, escucha profesional ni round trip en Pro Tools.
El Intel físico con Sequoia 15.7.5 sigue pendiente.

## Referencia histórica: beta 0.1, runtime 1.24.2

App universal ARM64/x86_64 en `paquete local previo de la beta 0.1`, unos 247 MB;
ZIP personal de unos 177 MB y checksum en `dist/SHA256.txt`.
Firma ad hoc local comprobada, sin notarización Developer ID.
El paquete se descomprimió en `build/relocated-package/` y su worker procesó
audio no nulo en ambas arquitecturas (x86_64 bajo Rosetta), usando únicamente
el runtime y modelos contenidos en esa copia. No precisa Python en destino.

## Comparación histórica con capturas de referencia CPU

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
  solapamientos, alineación y ganancia global; capturas de la aplicación de referencia.
- Cada carpeta contiene `divergences.csv`: **cero filas fuera de tolerancia**.
  `difference-manifest.json` y los NPZ por stem conservan todos los valores
  originales/nativos y todas las máscaras de diferencias IEEE754, además de
  las máscaras de tolerancia y hashes. El caso ampliado conserva sus NPZ.

El corpus cubre silencio, ceros con signo, impulso mínimo, límites 511/512/513,
8/16/44.1/48 kHz, dual mono y límites de bloques de refinado y separación.
Son fixtures sintéticos; no representan una validación de voces ni del acting.

## Rendimiento y recursos

| Entrada, motor ya cargado | Nuevo worker CPU | Referencia CPU, interfaz real |
|---|---:|---:|
| 8 s | 18.29 s | 20.40 s |
| 30 s | 83.63 s | 91.23 s |

En estas mediciones queda por debajo del objetivo de no superar 2× el tiempo de la referencia CPU.
Carga inicial del nuevo motor: 2.18 s en esa serie. Cuatro hilos por sesión,
ejecución secuencial, optimización ORT completa y spinning desactivado.
Prueba inicial aislada del modelo principal: ~55 s/8 s con un hilo frente a
~17 s con cuatro, tomada durante compilación; no se usa como benchmark final.

La nueva app mide dentro del worker; la referencia se midió desde Open hasta la
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
   la referencia CPU. No se ha utilizado material de producción privado.
3. Verificar el round trip en Pro Tools y el BWF dentro de su flujo real.
4. Prueba sostenida con audio no nulo hasta 30 minutos y evaluación de CoreML.
   La beta funciona en CPU; no incluye aceleración GPU habilitada ni probada.

La app está implementada y probada localmente como beta personal. Estos
pendientes impiden declararla equivalente en calidad profesional o validada
en ambos equipos físicos.
