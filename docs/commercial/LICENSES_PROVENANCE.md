# Licencias y procedencia / Licensing and provenance

Versión documental / Document revision: 1.3 | 2026-11-04 | Referencia / Baseline: Cauces 0.4.2, build 6

Preparación posterior: [candidato local 0.4.2 build 7](../../RELEASE.md), con avisos
actualizados y entrega de fuentes. Las menciones a paquetes intactos se refieren
al histórico build 6; los permisos pendientes de modelos siguen pendientes.
Later preparation: local build 7 has updated notices and source delivery;
unchanged historical-package references below concern build 6, not this new candidate.

## ES / EN - Licencia del material propio / Original-material licence

El titular aprobó el 04-11-2026 **GPL-3.0-only** para el código, documentación y
artwork propios. Ver [LICENSE](../../LICENSE), [COPYRIGHT](../../COPYRIGHT) y
[alcance](../../LICENSE_SCOPE.md). Bibliotecas, avisos de terceros y assets de
modelos mantienen su tratamiento separado. La declaración del titular de que no
incorporó otras contribuciones no acredita la autoría de conversiones o pesos.
Se registra como declaración, no como verificación independiente ni DCO
retroactivo. Las futuras aportaciones se rigen por [CONTRIBUTING](../../CONTRIBUTING.md).

On 2026-11-04 the owner approved **GPL-3.0-only** for original code, documentation
and artwork. Third-party libraries, notices and model assets remain separate.
The owner's statement about no additional contributions does not establish
conversion/weight authorship, independently verify rights or retroactively
certify DCO compliance. Future contributions follow the policy linked above.

## ES - Corrección de procedencia y alcance

La revisión del 04-11-2026 reemplaza la atribución anterior de conversión ONNX y
refinador a GuerraMagica como autoría acreditada. Los archivos proceden de una
distribución local de terceros: sus cuatro assets coinciden byte a byte por
SHA-256 con los empleados por Cauces. Esa coincidencia identifica una procedencia
de distribución; no prueba quién los creó, entrenó o posee sus derechos.
Los originales y el expediente técnico se conservan localmente.

**Modelo de banda baja:** MossFormer2_SS_16K, Alibaba Speech Lab. Tanto la ficha
upstream como el aviso de la distribución de origen declaran **Apache-2.0** para
este modelo. Por tanto, no corresponde describirlo como un modelo sin licencia.
Apache-2.0 permite formas fuente/objeto y modificaciones; el paso a ONNX no exige
por sí mismo una licencia distinta. Permanece pendiente precisar el alcance de
la declaración sobre aportaciones específicas del exportador. Conservar texto de
licencia, atribuciones y avisos de cambios aplicables (fuentes S1, S2, S10, S14).

La distribución registra ClearerVoice-Studio en la revisión
`6b3774dc79c46ae8bed2a4fa5f706f0ac8c75c61` y el checkpoint fuente con SHA-256
`00a3a48bda492db1e829b85dd443f8f43a43039a3e90f1a24962ea9caf14a11a`.
La huella coincide con la publicada para el checkpoint oficial; no demuestra
equivalencia tensor por tensor ni identifica el exportador usado. Los scripts
originales de esta conversión no se han localizado.

Este inventario es de componentes directos, no un SBOM transitivo exhaustivo ni
una aprobación jurídica. Ver [inventario](component-inventory.json),
[huellas históricas](asset-manifest.json) y [fuentes](SOURCES.md). La licencia de
ONNX Runtime es la del motor de ejecución, no la de los modelos. No se incorporan
assets ni supuestos de licencia de MULTI SPEAKER SEPARATION LAB.

## EN - Provenance correction and scope

The 2026-11-04 review supersedes earlier conversion/refiner attribution to
GuerraMagica as established authorship. The assets came from a local third-party
distribution: SHA-256 matches identify all four files used by Cauces. This
establishes distribution provenance, not who created/trained them or owns their
rights. Original notices and the technical evidence remain locally retained.

**Low-band model:** Alibaba Speech Lab's MossFormer2_SS_16K. Both the upstream
card and the source distribution declare **Apache-2.0** for it. It must not be
described as having no licence declaration. Apache-2.0 permits source/object
forms and modifications; ONNX conversion alone does not require another licence.
The declaration's scope over specific exporter contributions still needs
clarification. Retain applicable licence, attribution and modification notices.

The source distribution records ClearerVoice-Studio revision
`6b3774dc79c46ae8bed2a4fa5f706f0ac8c75c61` and the source checkpoint fingerprint
listed above. The match with the official checkpoint does not prove tensor
equivalence or identify the exporter used. Its original scripts were not found.
This is a direct inventory, not a complete transitive SBOM or legal clearance.
The runtime licence does not license models; no LAB assets are introduced.

## ES / EN - Componentes directos / Direct components

| Componente / Component | Licencia y evidencia / Licence and evidence |
|---|---|
| App, DSP, documentación y artwork propios / Original app, DSP, docs and artwork | GPL-3.0-only; aprobación del titular / owner approval, 2026-11-04 |
| MossFormer2_SS_16K, Alibaba Speech Lab | Apache-2.0 declarada upstream y en origen / declared upstream and in source distribution |
| Conversión ONNX / ONNX conversion | Autoría no acreditada; alcance sobre aportaciones de exportación pendiente / authorship unestablished; scope over exporter contributions pending |
| Refinador / Refiner | Autoría, titularidad y permisos pendientes / authorship, ownership and permissions pending |
| ONNX Runtime 1.31.1, Microsoft | MIT y ThirdPartyNotices / MIT and third-party notices |
| nlohmann/json 3.11.3, Niels Lohmann | MIT; reconciliar aviso con header compilado / reconcile notice with compiled header |
| Frameworks Apple / Apple frameworks | Enlazados al sistema, sin redistribuir SDK / system-linked; no SDK redistribution |

## ES - Refinador de alta frecuencia de Cauces

**Estado:** aviso provisional; revisión de permisos pendiente. Se conserva como
componente necesario del procesamiento actual, sin modificar ni retirar sus pesos.

**Procedencia:** distribución local de terceros, incorporada a Cauces 0.4.2.
**Autoría del refinador y titularidad de sus pesos:** no acreditadas con la
documentación examinada. La declaración anterior del titular no las verifica.

Archivos implicados:

- `refiner.onnx`.
- Sus 13 tensores externos en `weights.bin`. Este archivo también contiene datos
  del separador: no se atribuye íntegramente al refinador.

SHA-256 de `refiner.onnx`:
`4d4d38f4ca538924118b79daf5e24f293fec6f04e5a6eca2aa36e04c8f23f9cb`

SHA-256 del archivo completo `weights.bin`:
`b1491a04c97baaa30ebecfc7290fc70daa9404774ace4495065f5243b4188889`

**Función:** refinamiento espectral de las estimaciones de separación usando la
mezcla original y las guías de separación.
**Licencia aplicable:** no determinada con la documentación disponible. No se
presupone que Apache-2.0 del modelo base cubra este refinador.
**Permiso de redistribución:** pendiente de acreditar mediante licencia o
autorización aplicable. No se afirma que tal licencia no exista.

La concesión GPL del material propio no cubre estos assets ni acredita sus
permisos. Su inclusión en una distribución pública sigue pendiente de resolver
estos derechos. Los hashes y referencias ONNX verifican identidad y dependencias,
no derechos. No se adopta «frozen Cauces v1 weights» como identificación original
verificada; tampoco se interpreta automáticamente el campo `source_hf_sha256`
como una procedencia de Hugging Face.

## EN - Cauces high-frequency refiner

**Status:** provisional notice; permissions review pending. It remains a required
component of current processing, with no removal or changes to its weights.
**Provenance:** local third-party distribution, incorporated into Cauces 0.4.2.
**Refiner authorship and weight ownership:** not established by the examined
documents. The earlier owner declaration does not verify them.

Assets are `refiner.onnx` and its 13 external tensors in `weights.bin`; that file
also contains separator data. SHA-256 fingerprints appear above. The refiner
performs spectral refinement using the original mixture and separation guides.
**Applicable licence:** undetermined; the base-model Apache-2.0 licence is not
presumed to cover it. **Redistribution permission:** pending evidence of an
applicable licence or authorisation. This does not assert that no licence exists.

The original-material GPL grant does not cover these assets or establish their
permissions. Public distribution including them remains unresolved. Hashes and
ONNX references identify files/dependencies, not rights. "Frozen Cauces v1 weights"
is not adopted as a verified original identifier; `source_hf_sha256` is not
automatically interpreted as Hugging Face provenance.

## ES / EN - Conversiones públicas independientes / Independent public conversions

S15-S17 identifican conversiones/exportadores públicos del modelo de banda baja
con declaraciones Apache-2.0. Son candidatos para estudiar una vía reproducible;
no acreditan la conversión actual ni los permisos del refinador. No se han
integrado, ejecutado ni validado perceptivamente. Sus contratos de entrada/salida
difieren; no se presentan como reemplazos directos.

S15-S17 identify public low-band conversions/exporters declaring Apache-2.0.
They are candidates for a reproducible route, not evidence for the current
conversion or refiner rights. They were not integrated, run or perceptually
validated. Their I/O contracts differ; they are not presented as drop-in replacements.

## ES / EN - Avisos y paquetes / Notices and packages

Los textos originales en `licenses/` permanecen intactos. Su `Model-NOTICE.txt`
es la copia histórica exacta de 0.4.2: contiene la atribución anterior, actualmente
no acreditada. El aviso fuente [actual](../../resources/Model-NOTICE.txt) y el
generador de metadatos la corrigen para futuros empaquetados. Su etiqueta de
integración ONNX v1 coincide con README y manifiesto; el aviso histórico dice v3.
No son pesos nuevos ni se han regenerado paquete, manifiesto de assets, PDF o ZIP.

La futura distribución debe incluir el texto completo Apache-2.0 asociado al
modelo base; su presencia en el dossier no prueba su inclusión en el bundle.
Completar SBOM por arquitectura y reconciliación de avisos antes de distribuir.
La licencia del material propio no relicencia los componentes de terceros.

Original texts in `licenses/` remain unchanged. Its `Model-NOTICE.txt` is the
exact historical 0.4.2 copy, retaining the earlier, currently unestablished
attribution. The current source notice and metadata generator correct it for
future packaging. Their ONNX v1 integration label matches README/manifest;
the historical notice says v3. No weights, packages, asset manifest, PDF or ZIP
were regenerated. A future distribution must include the full Apache-2.0 text
associated with the base model; its dossier copy does not establish bundle
inclusion. Architecture SBOM and notice reconciliation remain pending.
