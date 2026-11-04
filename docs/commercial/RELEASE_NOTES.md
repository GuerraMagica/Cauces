# Notas de versión / Release notes

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## Corrección documental / Documentation correction - 2026-11-04

La atribución histórica de conversión y refinador que figura abajo no está
acreditada y no se adopta como autoría verificada. La revisión actual reconoce
Apache-2.0 para el modelo de banda baja y mantiene pendientes el alcance sobre
aportaciones específicas del exportador y los permisos del refinador.
Ver [procedencia](LICENSES_PROVENANCE.md). El paquete histórico no se modifica.

The historical conversion/refiner attribution below is unestablished and is not
adopted as verified authorship. The current review records Apache-2.0 for the
low-band model; scope over specific exporter contributions and refiner permissions
remain pending. See provenance above. The historical package is unchanged.

## ES - Referencia personal 0.4.2, build 6 (02-11-2026)

El paquete histórico universal incorporó una atribución de conversión ONNX y
refinador a GuerraMagica según declaración del titular. Modelos, pesos, biblioteca numérica,
worker y runtime coinciden byte a byte con 0.4.1. No cambia la calidad ni el
algoritmo. La versión sigue firmada ad hoc sin notarización comercial.

0.4.1 corrigió lectura WAV directa mediante descriptor, sin reapertura /dev/fd.
0.4 incorporó Settings de Output/Sample rate. 0.3 introdujo diseño Flow e inglés
en la interfaz. 0.2 integró controles de seguridad y ORT 1.31.1. Esta historia no
significa que todas las versiones fueran distribuciones comerciales.

Conocidos: dos voces estimadas más residual; sin estéreo real; acting y drivers
necesitan escucha/aceptación manual. El problema perceptivo de reproducción no
está declarado resuelto. Intel físico y Pro Tools permanecen pendientes.
La documentación comercial posterior no altera el ZIP personal 0.4.2.

## EN - Personal reference 0.4.2, build 6 (2026-11-02)

The historical universal package attributed ONNX conversion/refiner to GuerraMagica
according to the owner declaration. Models, weights, numerical library, worker
and runtime are byte-identical to 0.4.1. Algorithm/quality are unchanged. This
version remains ad hoc signed without commercial notarization.

0.4.1 fixed direct-descriptor WAV access without reopening /dev/fd. 0.4 added
Output/Sample rate Settings. 0.3 introduced Flow design and English UI. 0.2 added
security controls and ORT 1.31.1. This history does not mean these were commercial
releases.

Known limits: two estimated voices plus residual, no true stereo, manual acting
and driver acceptance needed. The reported playback perception issue is not
marked resolved. Physical Intel and Pro Tools remain pending. Later commercial
documentation does not change the personal 0.4.2 ZIP.

## ES / EN - Plantilla de publicación / Future release template

Versión/version: {{RELEASE_VERSION}}; fecha/date: {{RELEASE_DATE}};
macOS/arquitecturas probadas / tested macOS/architectures: {{TESTED_PLATFORMS}}.
Cambios/changes: {{RELEASE_CHANGES}}. Límites conocidos/known issues:
{{RELEASE_KNOWN_ISSUES}}. Migración/migration: {{MIGRATION_NOTES}}.
Hash/canal de descarga / hash/download channel: {{DOWNLOAD_REFERENCE}}.
Nunca copiar un PASS de una build distinta. / Never copy PASS from another build.
