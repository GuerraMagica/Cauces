# Dossier técnico y de seguridad / Technical and security dossier

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## ES - Arquitectura y contrato de audio

Aplicación SwiftUI/AppKit con AVAudioEngine para preescucha y Core Audio para
salida/reloj. Un worker C++ persistente ejecuta la separación; la biblioteca C
pública permite integración externa y no sandboxea por sí sola a su anfitrión.
El protocolo es JSONL local por pipes, sin servidor HTTP. El empaquetado incluye
modelos, runtime y licencias; Python solo interviene en desarrollo y pruebas.

La mezcla pasa a 16 kHz; el separador usa bloques de 128000 muestras y avance de
96000, con alineación de voces por solapamiento y calibración conjunta de ganancia.
El refinado se hace a 48 kHz, bloques de 144000 y avance de 120000; FFT 2048,
hop 480, 1025 bins. El resultado vuelve al sample rate de entrada. Residual =
entrada - (voz1 + voz2). Se retienen frames/canales y BWF time_reference; no se
promete otra metadata. Nada de este dossier modifica estos cálculos.

ONNX Runtime CPU 1.31.1; cuatro threads intra-op, uno inter-op, ejecución
secuencial, optimización completa y spinning desactivado. Selective FP16 describe
almacenamiento de pesos convertido; no significa convertir toda la aritmética a
FP16. El perfil del manifiesto conserva CPU/refinador FP32 según sus campos.
El grafo separator_gpu.onnx se incluye pero no se usa en este camino CPU.

## EN - Architecture and audio contract

SwiftUI/AppKit application with AVAudioEngine preview and Core Audio output/clock
selection. A persistent C++ worker separates audio; the public C library supports
external integration and does not independently sandbox its host. JSONL uses
local pipes, with no HTTP server. Models, runtime and licences are bundled;
Python is a development/test tool only.

The mixture is resampled to 16 kHz. The separator uses 128000-sample blocks and a
96000-sample stride, overlap-based speaker alignment and common gain calibration.
Refinement runs at 48 kHz using 144000-sample blocks and a 120000-sample stride;
FFT 2048, hop 480, 1025 bins. Results return to the input rate. Residual = input - (voice1 + voice2). Frames/channels and BWF time_reference
are retained; other metadata is not promised. This dossier changes none of the math.

ONNX Runtime CPU 1.31.1 uses four intra-op threads, one inter-op thread,
sequential execution, full optimization and disabled spinning. Selective FP16
refers to converted weight storage, not an all-FP16 pipeline. The manifest keeps
its existing CPU/refiner FP32 profile. separator_gpu.onnx is included but is not
used in the CPU path.

## ES - Propiedades y límites de seguridad

La GUI y worker llevan App Sandbox sin entitlements de cliente/servidor de red;
telemetría ORT desactivada. No hay cuentas, nube, descarga, updater ni activación
en ejecución. La GUI obtiene acceso al archivo mediante el selector y crea una
copia privada verificada; no presupone herencia de concesiones dinámicas al hijo.
La política rechaza volúmenes no locales, dataless y raíces de nube reconocidas;
no controla otros procesos sincronizadores ni configuraciones desconocidas.

Temporales con identidad/dev/inode y descriptores anclados; sin seguimiento de
symlinks. Lectura WAV mediante pread sobre descriptor regular/no bloqueante.
Modelos y pesos se verifican por SHA-256 y se pasan a ORT desde los mismos bytes.
API C y worker comparten la verificación. JSON limitado a 1 MiB/profundidad 16 y
IDs enteros acotados; exportación mediante copia verificada y publicación exclusiva.
Cancelar mata/espera al worker nativo y sincroniza limpieza de copias pendientes.

Límites: carreras frente a un escritor hostil del mismo UID no eliminadas;
excepción de library validation del worker ad hoc; sin borrado seguro SSD;
servicios de macOS fuera de la frontera. El modelo cargado se conserva en memoria
hasta cerrar el worker. No se ha realizado una auditoría exhaustiva de todas las
dependencias. Un escaneo o una suma no garantizan ausencia de vulnerabilidades.

## EN - Security properties and boundaries

GUI and worker have App Sandbox without network client/server entitlements; ORT
telemetry is disabled. No account, cloud, downloader, updater or activation runs
inside the app. The GUI obtains file access through the picker and creates a
verified private copy; it does not assume dynamic grants pass to a child. Policy
rejects non-local volumes, dataless files and recognised cloud roots; unrelated
sync processes and unknown configurations remain outside its control.

Temporary cleanup uses pinned descriptors and dev/inode identity without following
symlinks. WAV uses pread on a regular nonblocking descriptor. Model SHA-256 checks
cover the same bytes passed to ORT; API C and worker share the gate. JSON is
bounded to 1 MiB/depth 16 and bounded integer IDs. Exports use verified copies and
exclusive publication. Cancellation kills/waits for the native worker and
synchronises pending-copy cleanup.

Remaining boundaries include hostile same-UID writers, the ad hoc worker library
validation exception, no secure SSD erasure, and external macOS services. Loaded
model bytes remain in worker memory until closure. Dependencies have not all been
exhaustively audited. A scan or checksum is not a vulnerability-free guarantee.

## ES / EN - Evidencia / Evidence

V: src/security.cpp, wav.cpp, model_assets.cpp, models.cpp, WorkerConnection.swift,
LocalFilePolicy.swift; resources/*.entitlements. H: docs/validation.md and local
evidence/security-regressions-20261101 and evidence/cauces-release-0.4.2. La evidencia
local no se distribuye aquí. / Local evidence is not included in this dossier.
