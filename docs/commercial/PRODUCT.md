# Ficha de producto / Product sheet

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## ES - Texto propuesto para clientes

**Cauces, de GuerraMagica Audio**, es una aplicación de escritorio para separar
una grabación con dos voces en Voice 1, Voice 2 y Residual. El audio se procesa en
el Mac; el motor no necesita cuentas, activación en línea ni servicios de nube.
Permite alternar las cuatro pistas en el mismo punto y exportar tres WAV float32.
La interfaz de la versión de referencia está en inglés; esta documentación es
bilingüe y no implica que exista una interfaz traducida al español.

Requisitos y límites de referencia: macOS 15 o posterior; ejecutables universales
ARM64/x86_64; inferencia CPU; WAV RIFF PCM16, PCM24 o float32; mono o dos canales
idénticos; 8-48 kHz; máximo 30 minutos y 1 GiB por archivo. Necesita espacio local
para temporales y exportación. No se ha establecido un mínimo comercial de RAM
ni una matriz completa de sistemas/drivers: publicarlos tras las pruebas.

Se conservan frecuencia, número de muestras y número de canales. Si existe BWF,
se conserva time_reference. No se promete preservar íntegramente iXML, UMID,
loudness ni metadata propietaria. La separación es una estimación: puede contener
bleed, artefactos o intercambios de identidad. El residual puede contener diálogo.
Conviene evaluar actuación, timbre, consonantes, respiraciones y colas antes de
incorporar el resultado a una entrega profesional.

## EN - Proposed customer copy

**Cauces by GuerraMagica Audio** is a desktop application that separates a
two-voice recording into Voice 1, Voice 2 and Residual. Audio is processed on your
Mac; the engine needs no account, online activation or cloud service. You can
switch between four aligned tracks and export three float32 WAV files. The
reference application UI is English; bilingual documentation does not imply a
Spanish-translated interface.

Reference requirements/limits: macOS 15 or later; universal ARM64/x86_64 binaries;
CPU inference; RIFF WAV PCM16, PCM24 or float32; mono or identical dual mono;
8-48 kHz; up to 30 minutes and 1 GiB per file. Local temporary/export space is
required. Commercial minimum RAM and a complete OS/driver matrix have not been
established and must be published after validation.

Sample rate, frame count and channel count are retained. BWF time_reference is
retained when present. Full iXML, UMID, loudness and proprietary metadata
retention is not promised. Separation is an estimate and may contain bleed,
artifacts or speaker swaps. Residual may contain dialogue. Review performance,
timbre, consonants, breaths and tails before professional delivery.

## ES - Límites de las afirmaciones comerciales

No anunciar: más de dos hablantes, estéreo real, limpieza perfecta, reconocimiento
fiable de personas, reconstrucción fiel de toda la interpretación, tiempo real,
GPU habilitada, plugin DAW, batch, certificación Pro Tools/Netflix o rendimiento
Intel físico medido. No confundir el nombre Multi-Speaker con separación de N
hablantes. Los 30/30 casos sintéticos históricos no son una puntuación de calidad.
No describir el aislamiento del proceso como garantía sobre otros sincronizadores.

## EN - Limits on commercial claims

Do not advertise more than two speakers, true stereo, perfect removal, reliable
person identification, complete performance reconstruction, real-time processing,
enabled GPU, DAW plug-in, batch operation, Pro Tools/Netflix certification or
measured physical-Intel performance. Multi-Speaker does not mean N-speaker
separation. The historical 30/30 synthetic cases are not a quality score. Process
network isolation is not a guarantee about other sync applications.
