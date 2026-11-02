# Validación y aceptación / Validation and acceptance

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## ES - Qué está demostrado y qué falta

H: registros del 02-11-2026 para 0.4.2: 8/8 CTest ARM64 y 8/8 x86_64/Rosetta,
transporte Swift en ambos, 36 rechazos individuales de assets, 100 WAV malformados,
paquete extraído fuera del proyecto y probes App Sandbox con red EPERM.
Exports de fixture: 44100 Hz, 352800 muestras. Los probes sustituyen el entry point
GUI de una copia; no son selección manual de archivos ni escucha profesional.
H: la auditoría de calidad previa comparó 30/30 casos sintéticos dentro de
atol=1e-5/rtol=1e-4, máximo 3.129243850708008e-06; no igualdad bit a bit general.
No se vuelven a ejecutar pruebas de audio por crear este dossier.

P: Intel físico/Sequoia 15.7.5, escucha autorizada de diálogo real, diferencias de
preview, desconexión física de interfaces y round trip Pro Tools. Un antiguo
PASS no se transfiere a un binario resignado o modificado sin comprobar su alcance.

## EN - Established evidence and remaining work

H: 2026-11-02 records for 0.4.2: 8/8 ARM64 and 8/8 x86_64/Rosetta CTest,
both Swift transports, 36 isolated asset rejections, 100 malformed WAVs,
relocated-package checks and App Sandbox probes with network EPERM. Fixture
exports: 44100 Hz, 352800 frames. Probes replace a test copy's GUI entry point;
they are not file-picker or professional listening acceptance.
H: the earlier quality audit compared 30/30 synthetic cases within
atol=1e-5/rtol=1e-4, maximum 3.129243850708008e-06; not general bitwise equality.
Creating this dossier does not rerun audio tests.

P: physical Intel/Sequoia 15.7.5, authorised real-dialogue listening, preview
perception, physical interface disconnect and Pro Tools round trip. Old PASS does
not automatically transfer to a changed/re-signed binary.

## ES - Campaña de aceptación propuesta

1. Fijar candidato por commit, SHA del ZIP, hashes de modelos, firma y macOS/driver.
   Usar copias de prueba autorizadas y conservar hashes/mtime de originales.
2. Matriz: ARM físico e Intel físico; macOS mínimo anunciado y cada sistema que se
   publique como compatible; salida integrada y al menos una interfaz profesional.
   Registrar RAM, CPU, disco, carga y reloj. Medir tiempos sin prometer una cifra
   a partir de inferencias bajo Rosetta o de silencio que omite el modelo.
3. Formatos: PCM16/PCM24/float32, 8/16/44,1/48 kHz, mono/dual mono, BWF64-bit
   time_reference. Probar límites, RF64/no admitidos, NaN/Inf, truncación, FIFO,
   falta de espacio, colisión, cancelación y segundo trabajo tras error.
4. Audio: voces de registros similares/diferentes, solapamientos, susurro, grito,
   respiraciones, consonantes y colas. Evaluar identidad y actuación, no solo bleed.
   Comparar mismos recortes/contexto, sin normalización oculta. Anotar muestras,
   juicio humano y ejemplos autorizados. No declarar ganador por un contador.
5. Reproductor: A/B de WAV exportados en un DAW, mismo dispositivo, frecuencia,
   nivel y posición; después comparar preview. Medir diferencias de nivel/espectro,
   SRC y alineación si son reproducibles. Conservar hallazgos aunque sean subjetivos.
6. Pro Tools: importar a origen BWF, verificar unidades y posición en muestras,
   canales/longitud/offset y escucha en mezcla. Documentar metadata que no se retiene.
7. Seguridad/paquete: suite existente, gate individual de assets, red denegada en
   padre/hijo, UI real de paneles, Gatekeeper activo, actualización y rollback
   sobre máquinas limpias sin vendor/build. Resolver cada FAIL antes de aprobar.

## EN - Proposed acceptance campaign

1. Freeze commit, ZIP SHA, model hashes, signature and OS/driver. Use authorised
   working copies and retain source hashes/mtime.
2. Matrix: physical ARM and Intel; advertised minimum macOS and each claimed
   supported OS; built-in output plus a professional interface. Record RAM, CPU,
   disk, load and clock. Do not infer performance from Rosetta or model-skipping silence.
3. Formats: PCM16/PCM24/float32; 8/16/44.1/48 kHz; mono/dual mono; BWF64-bit
   time_reference. Cover boundaries, RF64/unsupported data, NaN/Inf, truncation,
   FIFO, low space, collisions, cancellation and recovery.
4. Audio: similar/different voice registers, overlap, whisper/shout, breaths,
   consonants and tails. Judge identity/performance, not bleed alone. Use identical
   excerpts/context and no hidden normalization. Record sample intervals, human
   judgments and authorised examples; event counts do not establish superiority.
5. Playback: compare exports in one DAW/output/rate/level/position, then preview.
   Measure level/spectrum, SRC and alignment differences when reproducible. Retain
   observations even where they require listening judgment.
6. Pro Tools: import at BWF origin; verify units, sample position, channels,
   length/offset and in-mix listening. State metadata not retained.
7. Security/package: run existing suites, asset gates, parent/child network denial,
   real file-picker workflow, Gatekeeper, upgrades and rollback on clean machines
   without vendor/build. Resolve every FAIL before approval.

Acta/record: [templates/ACCEPTANCE_RECORD.md](templates/ACCEPTANCE_RECORD.md).
