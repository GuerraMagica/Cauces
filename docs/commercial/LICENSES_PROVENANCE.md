# Licencias y procedencia / Licensing and provenance

Versión documental / Document revision: 1.2 | 2026-11-04 | Referencia / Baseline: Cauces 0.4.2, build 6

## ES / EN - Licencia del material propio / Original-material licence

El titular aprobó el 04-11-2026 **GPL-3.0-only** para el código, documentación y
artwork propios del repositorio. Ver [LICENSE](../../LICENSE),
[COPYRIGHT](../../COPYRIGHT) y [alcance](../../LICENSE_SCOPE.md). Bibliotecas,
textos de licencia de terceros, modelos, conversiones, refinador y pesos mantienen
su tratamiento separado. Los derechos pendientes del refinador siguen pendientes.

El titular declara que no ha incorporado aportaciones adicionales de otros autores
aparte de los componentes de terceros ya identificados. Se registra como D, no
como verificación independiente de titularidad ni como un DCO retroactivo.
Las futuras contribuciones se rigen por [CONTRIBUTING](../../CONTRIBUTING.md).

On 2026-11-04 the owner approved **GPL-3.0-only** for original repository code,
documentation and artwork. See the grant, licence and scope linked above.
Third-party libraries/licence texts and model assets remain separate. Refiner
rights are still pending. The owner declares no additional work by other authors
beyond the identified third-party components; this is a D statement, not
independent ownership verification or retroactive DCO certification.

## ES - Estado y alcance

Este inventario documenta componentes directos y evidencias disponibles; NO es
un SBOM transitivo exhaustivo ni una aprobación jurídica. Consulta los hashes
exactos en asset-manifest.json, el inventario en component-inventory.json y las
fuentes S1-S5/S10 en SOURCES. El modelo comercial de la app propia no cambia las
licencias de sus dependencias.

D: GuerraMagica declara haber desarrollado conversión ONNX y refinador el
02-11-2026. Falta adjuntar la declaración firmada, fuentes/exportadores,
identificación de contribuyentes y, si corresponde, derechos de los pesos o datos
utilizados. No se afirma que GuerraMagica entrenara el checkpoint base Alibaba.
El registro de propiedad intelectual no es un requisito constitutivo en España;
puede servir como evidencia adicional, sin sustituir las licencias ajenas.

H: los informes previos registran coincidencia SHA-256 del checkpoint fuente con MossFormer2_SS_16K;
la ficha upstream declara Apache-2.0. Esto no acredita por sí solo equivalencia de
todos los tensores convertidos. Mantener atribuciones, licencia y avisos de cambios
aplicables a la conversión. Las licencias principales de ONNX Runtime y JSON son
MIT; conservar copyright y permisos junto con los avisos transitivos pertinentes.

No copiar condiciones del LAB ni asumir que sus siete motores se distribuyen
con Cauces. No se incorporan modelos, pesos, Python, Torch o MLX de ese proyecto.

## EN - Status and scope

This inventory records direct components and available evidence; it is NOT an
exhaustive transitive SBOM or legal clearance. Exact hashes are in
asset-manifest.json, inventory in component-inventory.json and sources S1-S5/S10
in SOURCES. The project's GPL grant does not replace dependency licences.

D: GuerraMagica declared authorship of the ONNX conversion and refiner on
2026-11-02. Attach the signed declaration, sources/exporters, contributor records
and relevant weight/data rights where applicable. No claim is made that
GuerraMagica trained Alibaba's base checkpoint. Spanish copyright registration is
not constitutive; it may add evidence without replacing third-party permissions.

H: earlier reports record a source-checkpoint SHA-256 match with MossFormer2_SS_16K; upstream
identifies Apache-2.0. This alone does not prove equivalence of every converted
tensor. Retain applicable attribution, licence and modification notices. ONNX
Runtime and JSON main licences are MIT; retain copyright/permissions and relevant
transitive notices.

Do not import LAB licensing assumptions: its seven engines are not Cauces's
payload. No LAB model, weight, Python, Torch or MLX runtime is added here.

## ES / EN - Componentes directos / Direct components

- App, DSP, documentación y artwork propios / Original app, DSP, documentation and
  artwork: GPL-3.0-only, aprobación del titular del 04-11-2026 / owner approval
  dated 2026-11-04; declaración de contribuciones arriba / contributor statement above.
- MossFormer2_SS_16K: Alibaba Speech Lab; Apache-2.0 declarada upstream / declared upstream.
- Conversión / ONNX conversion: GuerraMagica, declaración del titular / owner declaration.
- refiner.onnx: GuerraMagica, declaración del titular / owner declaration.
- ONNX Runtime 1.31.1: Microsoft, MIT más ThirdPartyNotices / plus third-party notices.
- nlohmann/json 3.11.3: Niels Lohmann, MIT; verificar correspondencia exacta de avisos
  con el header compilado / verify notices against the compiled header.
- Frameworks Apple / Apple frameworks: enlazados al sistema; no redistribuimos el SDK
  / system-linked; no Apple SDK redistribution in the package.

## ES - Refinador de alta frecuencia de Cauces

**Estado:** documentación provisional de procedencia y derechos.

**Procedencia inmediata:** distribución local de Cauces 0.4.2, de GuerraMagica Audio.

**Autoría declarada del refinador:** GuerraMagica, según declaración del titular
del proyecto de fecha 02-11-2026.

**Autoría y titularidad de los pesos subyacentes:** pendientes de acreditación
documental. La declaración anterior no constituye por sí sola una comprobación
independiente de su procedencia ni de los derechos de redistribución.

Archivos implicados:

- `refiner.onnx`.
- Los 13 tensores externos que este modelo referencia en `weights.bin`. Este
  archivo también contiene datos utilizados por el separador; no se atribuye
  íntegramente al refinador.

SHA-256 de `refiner.onnx`:
`4d4d38f4ca538924118b79daf5e24f293fec6f04e5a6eca2aa36e04c8f23f9cb`

SHA-256 del archivo completo `weights.bin`:
`b1491a04c97baaa30ebecfc7290fc70daa9404774ace4495065f5243b4188889`

**Función:** refinamiento espectral de las estimaciones de separación, utilizando
la mezcla y las guías obtenidas durante el procesamiento.

**Licencia aplicable a estos assets:** no determinada con la documentación
examinada. No se presupone que la licencia del modelo base MossFormer2 cubra
este refinador.

**Permiso de redistribución:** pendiente de acreditar mediante una licencia o
autorización aplicable.

Esta nota documenta el estado de la información disponible y no concede permisos
de redistribución. La concesión GPL-3.0-only del material propio del proyecto no
cubre estos assets ni acredita sus permisos. Su incorporación a una distribución pública queda
pendiente de resolver y documentar estos derechos.

Verificación local del 04-11-2026: hashes y referencias de los inicializadores
externos del grafo ONNX. Estos controles identifican archivos y dependencias;
no acreditan titularidad ni licencia. La etiqueta «frozen Cauces v1 weights» no se
ha corroborado en el grafo ni en los manifiestos examinados y no se adopta como
identificación verificada.

## EN - Cauces high-frequency refiner

**Status:** provisional provenance and rights documentation.

**Immediate provenance:** local Cauces 0.4.2 distribution, GuerraMagica Audio.

**Declared refiner authorship:** GuerraMagica, according to the project owner's
declaration dated 2026-11-02.

**Underlying weights' authorship and ownership:** documentary evidence pending.
The declaration alone is not an independent verification of their provenance or
redistribution rights.

Assets concerned:

- `refiner.onnx`.
- The 13 external tensors this model references in `weights.bin`. That file also
  contains data used by the separator; it is not attributed wholly to the refiner.

SHA-256 of `refiner.onnx`:
`4d4d38f4ca538924118b79daf5e24f293fec6f04e5a6eca2aa36e04c8f23f9cb`

SHA-256 of the complete `weights.bin` file:
`b1491a04c97baaa30ebecfc7290fc70daa9404774ace4495065f5243b4188889`

**Function:** spectral refinement of separation estimates using the mixture and
the guides obtained during processing.

**Applicable asset licence:** undetermined from the documentation examined. The
MossFormer2 base-model licence is not presumed to cover this refiner.

**Redistribution permission:** pending evidence of an applicable licence or
authorisation.

This note records the available information and grants no redistribution rights.
The project's GPL-3.0-only grant for original material does not cover these assets
or establish their permissions. Their inclusion in a
public distribution remains pending resolution and documentation of these rights.

Local verification on 2026-11-04 covered hashes and external-initializer references
in the ONNX graph, not ownership or licensing. The label "frozen Cauces v1 weights"
was not corroborated in the graph or manifests examined and is not adopted as a
verified identifier.

## ES - Avisos que acompañarán al paquete

Los textos originales en licenses se conservan sin alterar. Model-NOTICE es la
copia histórica exacta del 0.4.2; `resources/Model-NOTICE.txt` incorpora el aviso
provisional anterior para futuros empaquetados. No se ha regenerado el paquete
0.4.2 ni alterado su manifiesto de assets. El encabezado de ambos avisos dice
ONNX v3 mientras el campo name del
manifest y README dicen ONNX v1. Son etiquetas de integración, no pesos nuevos.
Resolver esta inconsistencia nominal antes de publicar; no renombramos ahora el
paquete ni los assets para ocultarla. El fichero Apache-2.0 se aporta al dossier;
comprobar que la futura distribución lo asocia inequívocamente al modelo base.

ThirdPartyNotices de ORT es una referencia upstream amplia: determinar qué
componentes se compilaron realmente y completar un SBOM trazable por arquitectura.
Revisar si el código upstream modificado requiere fuentes, avisos o condiciones
adicionales. La concesión GPL-3.0-only del material propio no relicencia estos
componentes. El borrador contractual no revoca derechos open source.

## EN - Notices to accompany the package

Original licence texts in licenses remain unchanged. Model-NOTICE is the exact
historical 0.4.2 copy; `resources/Model-NOTICE.txt` adds the provisional notice above
for future packaging. The 0.4.2 package and asset manifest were not regenerated
or changed. Both notice headings say ONNX v3 while the manifest name and README
say ONNX v1. These are integration labels, not new weights. Resolve that naming
inconsistency before publication; this dossier does not silently rename the app
or assets. Apache-2.0 is supplied in the dossier; ensure a future distribution
clearly associates it with the base model.

ORT ThirdPartyNotices is a broad upstream reference: determine actual compiled
components and complete an architecture-traceable SBOM. Check source/notice
requirements of modified upstream code. The GPL-3.0-only grant for original
material does not relicense these components. Draft terms do not revoke
open-source rights.
