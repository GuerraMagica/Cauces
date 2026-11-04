# Fuentes y trazabilidad / Sources and traceability

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## ES - Uso y fecha

Consulta documental general: 02-11-2026; seguimiento de licencias ONNX: 04-11-2026. Las referencias primarias apoyan la preparación;
comprobar versión, ámbito y modificaciones al publicar. No se presentan resúmenes
como asesoría individual. Los enlaces ELI oficiales pueden exigir JavaScript;
para las fechas CRA se consultó además la explicación de la Comisión. No se
realizaron búsquedas de marcas ni se completó un examen de derechos de terceros.

## EN - Use and date

General review date: 2026-11-02; ONNX licensing follow-up: 2026-11-04. Primary references support preparation; recheck
version, scope and amendments before publication. Summaries are not individual
legal advice. Official ELI links may require JavaScript; CRA dates were also
checked against Commission guidance. No trademark search or complete rights
clearance was performed.

## Referencias / References

- S1 - [MossFormer2_SS_16K, Alibaba Speech Lab](https://huggingface.co/alibabasglab/MossFormer2_SS_16K): ficha y licencia declarada / model card and declared licence.
- S2 - [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0): redistribución, atribución y cambios / redistribution, attribution and changes.
- S3 - [ONNX Runtime 1.31.1 LICENSE](https://github.com/microsoft/onnxruntime/blob/v1.31.1/LICENSE): MIT; avisos locales / local third-party notices supplied separately.
- S4 - [nlohmann/json 3.11.3 LICENSE](https://github.com/nlohmann/json/blob/v3.11.3/LICENSE.MIT): MIT; contrastar copia local / reconcile bundled copy.
- S5 - [Registro de Propiedad Intelectual, Ministerio de Cultura](https://www.cultura.gob.es/cultura/propiedadintelectual/la-propiedad-intelectual/preguntas-mas-frecuentes/registro.html): registro voluntario / voluntary registration.
- S6 - [TRLGDCU, BOE](https://www.boe.es/buscar/act.php?id=BOE-A-2007-20555): arts. 97-104 y título de conformidad / precontract, withdrawal and conformity provisions.
- S7 - [Directiva UE 2019/770](https://eur-lex.europa.eu/eli/dir/2019/770/oj): contenidos y servicios digitales / digital content and services; transposición aplicable / relevant national implementation.
- S8 - [RGPD](https://eur-lex.europa.eu/eli/reg/2016/679/oj) y [guía EDPB para pequeñas empresas](https://www.edpb.europa.eu/sme/be-compliant/respect-individuals-rights_en): privacidad y derechos / privacy and rights.
- S9 - [Apple Developer ID](https://developer.apple.com/developer-id/) y [notarización](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution): distribución macOS / macOS distribution.
- S10 - Evidencia local / local evidence: comparación SHA-256 de los cuatro assets con una distribución local de terceros y aviso original retenido en el expediente privado, revisión 04-11-2026 / four-asset SHA-256 comparison with a local third-party distribution and original notice retained in private evidence, reviewed 2026-11-04. La coincidencia no prueba autoría / the match does not prove authorship. Correcciones propias / project corrections: resources/Model-NOTICE.txt, scripts/model_manifest.py y / and docs/validation.md. La atribución del titular del 02-11-2026 no se adopta como verificada / the 2026-11-02 owner attribution is not adopted as verified.
- S11 - [Marco IA, Comisión Europea](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai): evaluación de uso/rol y obligaciones / intended-use/role assessment.
- S12 - [CRA, texto legal](https://eur-lex.europa.eu/eli/reg/2024/2847/oj), [resumen Comisión](https://digital-strategy.ec.europa.eu/en/policies/cra-summary) y [notificación](https://digital-strategy.ec.europa.eu/en/policies/cra-reporting): alcance y calendario / scope and timetable.

- S13 - [Cierre ODR / ODR closure, Comisión Europea](https://consumer-redress.ec.europa.eu/site-relocation_en): cierre el 20-07-2025 y vías actuales / closure on 2025-07-20 and current redress routes.

## ES / EN - Evidencias históricas / Historical records

Documentación del repositorio / Repository documentation: docs/validation.md.
Registros locales ignorados / ignored local records: evidence/cauces-quality-audit-20261028,
evidence/security-regressions-20261101, evidence/cauces-release-0.4.2.
No se incluyen audios ni logs privados. / No audio or private logs are included.

- S14 - [ClearerVoice-Studio LICENSE, revisión registrada / recorded revision](https://github.com/modelscope/ClearerVoice-Studio/blob/6b3774dc79c46ae8bed2a4fa5f706f0ac8c75c61/LICENSE): Apache-2.0 del código / code licence. [Checkpoint oficial / official checkpoint](https://huggingface.co/alibabasglab/MossFormer2_SS_16K/tree/407cb030cd66340918ebb6c8cc63b18f8592cdbe): coincidencia de huella publicada, no equivalencia de tensores / published fingerprint match, not tensor equivalence.
- S15 - [iazShadow, conversión ONNX independiente / independent ONNX conversion](https://huggingface.co/iazShadow/mossformer2-ss-16k-onnx/tree/291614c7539242b840e9662f18f8b2d551255461): README y LICENSE Apache-2.0, incluida declaración para conversión/metadatos / Apache-2.0 README and LICENSE, including a conversion/metadata declaration. No integrada ni ejecutada / not integrated or run.
- S16 - [mhavo, conversión ONNX independiente / independent ONNX conversion](https://huggingface.co/mhavo/mossformer2-ss-16k-onnx/tree/3be7f95237b5121caf41dec4c62b0af341a640af): ficha Apache-2.0, sin LICENSE separado en la revisión examinada / Apache-2.0 card, no separate LICENSE at the examined revision. No integrada ni ejecutada / not integrated or run.
- S17 - [DakeQQ, exportador público / public exporter](https://github.com/DakeQQ/Audio-Denoiser-ONNX/blob/4bb7f6c0f46dd5cb69c2fca5bbf613d943779357/MossFormer2_SS_16K/Export_MossFormer2_SS_16K.py) y / and [LICENSE](https://github.com/DakeQQ/Audio-Denoiser-ONNX/blob/4bb7f6c0f46dd5cb69c2fca5bbf613d943779357/LICENSE): Apache-2.0 en raíz / at repository root. Sin auditoría integral de dependencias ni ejecución; no se identifica como el exportador original / no full dependency audit or execution; not identified as the original exporter.
