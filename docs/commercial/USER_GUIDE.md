# Manual de usuario / User guide

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## ES - Instalación y primera apertura

Obtén el paquete del canal autorizado por el vendedor y compara su SHA-256 con
una referencia publicada por un canal de confianza independiente. Una suma
coincidente prueba integridad respecto de esa referencia, no quién es el autor.
Descomprime el ZIP y conserva la app completa. Puedes copiarla a Aplicaciones;
no necesita Python ni instalación de modelos aparte. Cierra cualquier versión
anterior antes de abrir otra con el mismo identificador.

La beta de referencia 0.4.2 tiene firma ad hoc, sin Developer ID ni notarización.
No es el paquete comercial firmado previsto. Una futura distribución comercial
se comprobará con Gatekeeper activo. Si macOS rechaza un paquete, verifica
origen/versión y consulta al soporte; no desactives las protecciones del sistema.
Antes de una sesión importante, prueba una copia corta de material autorizado.

## EN - Installation and first launch

Obtain the package through the seller's authorised channel and compare SHA-256
with a reference published through an independent trusted channel. A matching
hash proves integrity against that reference, not the author's identity.
Extract the ZIP and keep the full app. You may copy it to Applications; Python
and separate model installation are unnecessary. Quit an older version before
opening another with the same bundle identifier.

Reference beta 0.4.2 is ad hoc signed, without Developer ID or notarization. It is
not the planned commercially signed package. Test future commercial releases
with Gatekeeper enabled. If macOS rejects a package, verify its origin/version
and contact support; do not disable system protection. Before a critical session,
test a short copy of authorised material.

## ES - Flujo de trabajo

1. Pulsa Open audio o arrastra un WAV compatible. Selecciona almacenamiento local
   no sincronizado. No se admiten RF64, archivos vacíos, estéreo distinto ni canales
   adicionales. Un WAV de mayor frecuencia debe prepararse en tu DAW sobre una copia.
2. Pulsa Separate voices. Espera al resultado o usa Cancel/Escape. Solo se procesa
   un trabajo cada vez. El archivo original no se sobrescribe.
3. Compara Original, Voice 1, Voice 2 y Residual. Espacio reproduce/pausa;
   Cmd+1 a Cmd+4 seleccionan pista; el cursor permite buscar el mismo instante.
4. En Cauces > Settings (Cmd+,), Output elige la salida de Cauces. System Default
   sigue la salida del sistema. Device default sigue el reloj sin solicitar otro.
   Una frecuencia explícita y Apply pueden cambiar el reloj compartido y afectar
   a otras apps. Cancel descarta la edición. No hay ajustes de entrada/MIDI/buffer.
5. Export audio crea una carpeta nueva <nombre>_separated con tres WAV float32:
   <nombre>_voice_1.wav, <nombre>_voice_2.wav y <nombre>_residual.wav. Una carpeta
   existente provoca error; elige otro destino. No hay normalización de pico al
   exportar. Se conserva la calibración interna propia del separador.
6. Importa los tres WAV en tu DAW, en la misma posición de origen. Comprueba
   duración, canales y BWF antes de moverlos. Escucha aislados y en contexto.

## EN - Workflow

1. Choose Open audio or drop a supported WAV. Use local, unsynchronised storage.
   RF64, empty files, non-identical stereo and extra channels are unsupported.
   Prepare a higher-rate source in your DAW using a working copy.
2. Choose Separate voices. Wait for the result or use Cancel/Escape. Only one
   operation runs at a time. The original is not overwritten.
3. Compare Original, Voice 1, Voice 2 and Residual. Space plays/pauses; Cmd+1 to
   Cmd+4 select a track; seek to compare the same moment.
4. In Cauces > Settings (Cmd+,), Output selects Cauces playback. System Default
   follows the system output. Device default follows the clock without requesting
   a rate. An explicit rate plus Apply may change the shared device clock and
   affect other apps. Cancel discards edits. Input/MIDI/buffer settings are absent.
5. Export audio creates a new <name>_separated folder with three float32 WAVs:
   <name>_voice_1.wav, <name>_voice_2.wav and <name>_residual.wav. Existing folders
   are not overwritten. Select a different destination after a collision. Export
   adds no peak normalization; the separator's existing internal calibration remains.
6. Import the WAVs into your DAW at the original position. Check length, channels
   and BWF before moving them. Listen in isolation and in context.

## ES - Resolución de problemas y privacidad

Si no abre el WAV, comprueba permisos, ubicación local, formato y versión de la
app. Si falta un modelo o falla su integridad, vuelve a obtener el paquete completo;
no sustituyas pesos por archivos de otro producto. Si falta espacio, usa otro disco
local con capacidad suficiente. Si el driver rechaza una frecuencia, elige Device
default o revisa su panel. Si desconectas una salida seleccionada, se pausa.

Para diferencias audibles, compara primero los WAV exportados en la misma sesión,
nivel, salida y frecuencia. Anota pérdida de voz, bleed, cambios de identidad y
artefactos con intervalos de muestras. Conserva los originales. No envíes diálogos
confidenciales a soporte por defecto: empieza con un ejemplo sintético y datos
mínimos. Los temporales se intentan limpiar en cancelación/cierre normal; un cierre
forzado puede dejarlos y no existe promesa de borrado seguro en SSD.

## EN - Troubleshooting and privacy

For import errors check permissions, local location, format and app version. If
models are missing or fail integrity checks, obtain the complete package again;
do not substitute another product's weights. Free local disk space when needed.
If a driver rejects a rate, choose Device default or inspect its control panel.
Disconnecting an explicitly selected output pauses playback.

For audible differences first compare exported WAVs in the same DAW session,
level, output and sample rate. Record missing speech, bleed, identity swaps and
artifacts using sample intervals. Keep originals. Do not send confidential
dialogue to support by default: begin with synthetic reproduction and minimal
diagnostics. Cancellation/normal closure attempt temporary cleanup; a forced
termination may leave private files and secure SSD erasure is not promised.
