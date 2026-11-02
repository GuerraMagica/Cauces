# Licencias y procedencia / Licensing and provenance

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

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
in SOURCES. A proprietary app licence does not replace dependency licences.

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

- App, DSP y artwork / App, DSP and artwork: código propio del proyecto; titularidad
  y contribuciones a confirmar / project-specific code; confirm rights/contributors.
- MossFormer2_SS_16K: Alibaba Speech Lab; Apache-2.0 declarada upstream / declared upstream.
- Conversión / ONNX conversion: GuerraMagica, declaración del titular / owner declaration.
- refiner.onnx: GuerraMagica, declaración del titular / owner declaration.
- ONNX Runtime 1.31.1: Microsoft, MIT más ThirdPartyNotices / plus third-party notices.
- nlohmann/json 3.11.3: Niels Lohmann, MIT; verificar correspondencia exacta de avisos
  con el header compilado / verify notices against the compiled header.
- Frameworks Apple / Apple frameworks: enlazados al sistema; no redistribuimos el SDK
  / system-linked; no Apple SDK redistribution in the package.

## ES - Avisos que acompañarán al paquete

Los textos originales en licenses se conservan sin alterar. Model-NOTICE es la
copia exacta del 0.4.2; su encabezado dice ONNX v3 mientras el campo name del
manifest y README dicen ONNX v1. Son etiquetas de integración, no pesos nuevos.
Resolver esta inconsistencia nominal antes de publicar; no renombramos ahora el
paquete ni los assets para ocultarla. El fichero Apache-2.0 se aporta al dossier;
comprobar que la futura distribución lo asocia inequívocamente al modelo base.

ThirdPartyNotices de ORT es una referencia upstream amplia: determinar qué
componentes se compilaron realmente y completar un SBOM trazable por arquitectura.
Revisar si el código upstream modificado requiere fuentes, avisos o condiciones
adicionales. No inventar una licencia de GuerraMagica ni aplicar MIT por defecto
al proyecto propio. El borrador contractual no revoca derechos open source.

## EN - Notices to accompany the package

Original licence texts in licenses remain unchanged. Model-NOTICE is copied
exactly from 0.4.2; its heading says ONNX v3 while the manifest name and README
say ONNX v1. These are integration labels, not new weights. Resolve that naming
inconsistency before publication; this dossier does not silently rename the app
or assets. Apache-2.0 is supplied in the dossier; ensure a future distribution
clearly associates it with the base model.

ORT ThirdPartyNotices is a broad upstream reference: determine actual compiled
components and complete an architecture-traceable SBOM. Check source/notice
requirements of modified upstream code. Do not invent a GuerraMagica licence or
apply MIT to the project by default. Draft terms do not revoke open-source rights.
