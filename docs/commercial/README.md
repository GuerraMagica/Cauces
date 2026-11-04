# Cauces - Dossier de distribución comercial / Commercial distribution dossier

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## Actualización de licencia / Licence update - 2026-11-04

El material propio del repositorio adopta GPL-3.0-only por aprobación del titular.
El [alcance actual](../../LICENSE_SCOPE.md) y [CONTRIBUTING](../../CONTRIBUTING.md)
prevalecen sobre decisiones de licencia que este dossier histórico dejaba abiertas.
Los borradores comerciales no condicionan los derechos GPL a una compra ni a
límites de puestos. Modelos y pesos conservan los permisos pendientes documentados;
no se ha generado una nueva app ni una nueva versión del PDF/ZIP del dossier.

Original repository material is now GPL-3.0-only by owner approval. The current
scope and contribution policy linked above supersede historical open licence
choices in this dossier. Draft sales terms do not make GPL rights conditional on
purchase or seat limits. Model/weight permissions remain separately documented;
no app or dossier PDF/ZIP was rebuilt.

## ES - Cómo utilizar este dossier

Paquete bilingüe de preparación para una posible venta de Cauces. La referencia
es la beta personal 0.4.2; crear documentación no la convierte en una versión
comercial aprobada. Los documentos jurídicos son BORRADORES y no deben publicarse
con campos pendientes. No hay una tienda, precio, suscripción, SLA o certificación
creados por este trabajo. No se ha cambiado ni vuelto a empaquetar la app.

Estados: **V** = verificado en código/artefactos; **H** = ejecución histórica
registrada; **D** = declaración del titular; **P** = pendiente de decisión o prueba.
La declaración de GuerraMagica sobre conversión/refinador se conserva como D;
no se sustituye por la antigua descripción de autor desconocido.

Orden recomendado: leer PRODUCT y USER_GUIDE; completar publisher-profile;
resolver LICENSES_PROVENANCE y LEGAL_REVIEW; revisar los borradores con asesoría;
ejecutar VALIDATION_PLAN y RELEASE_RUNBOOK antes de autorizar una venta.
El precio, la licencia y las promesas de soporte se deciden por separado de las
pruebas técnicas. El índice distingue documentos para clientes de documentos
internos; no distribuir el dossier interno entero como condiciones de compra.

## EN - How to use this dossier

Bilingual preparation pack for a possible sale of Cauces. The baseline is personal
beta 0.4.2; documentation does not turn it into an approved commercial release.
Legal documents are DRAFTS and must not be published with unresolved fields.
This work creates no store, price, subscription, SLA or certification and does not
change or repackage the application.

Status: **V** = verified in code/artifacts; **H** = recorded historical execution;
**D** = owner declaration; **P** = pending decision or test. GuerraMagica's
conversion/refiner authorship remains a D statement, not an unknown-author claim.

Read PRODUCT and USER_GUIDE; complete publisher-profile; resolve
LICENSES_PROVENANCE and LEGAL_REVIEW; have the drafts reviewed; then run
VALIDATION_PLAN and RELEASE_RUNBOOK before approving sales. Decide pricing,
licensing and support commitments separately from technical acceptance. The
index separates customer material from internal records: do not distribute the
entire internal dossier as purchase terms.

## Índice / Index

- [Decisiones antes de vender / Pre-sale decisions](READINESS.md) - empezar aquí / start here.

- [Ficha y afirmaciones de producto / Product and claims](PRODUCT.md) - clientes / customer draft.
- [Manual / User guide](USER_GUIDE.md) - clientes / customer draft.
- [Notas de versión / Release notes](RELEASE_NOTES.md) - clientes / customer draft.
- [Condiciones y licencia / Terms and licence](TERMS_DRAFT.md) - borrador jurídico / legal draft.
- [Privacidad / Privacy](PRIVACY_DRAFT.md) - borrador jurídico / legal draft.
- [Soporte, actualizaciones y devoluciones / Support, updates and refunds](SUPPORT_REFUNDS_DRAFT.md) - borrador / draft.
- [Técnica y seguridad / Technical and security dossier](TECHNICAL_SECURITY.md) - interno / internal.
- [Licencias y procedencia / Licensing and provenance](LICENSES_PROVENANCE.md) - interno y avisos / internal and notices.
- [Publicación y firma / Release and signing](RELEASE_RUNBOOK.md) - interno / internal.
- [Validación y aceptación / Validation and acceptance](VALIDATION_PLAN.md) - interno / internal.
- [Mantenimiento y traspaso / Maintenance and handover](MAINTENANCE_HANDOVER.md) - interno / internal.
- [Revisión jurídica y regulatoria / Legal and regulatory review](LEGAL_REVIEW.md) - interno / internal.
- [Fuentes / Sources](SOURCES.md) - referencias / references.
- [Datos del vendedor / Publisher profile](publisher-profile.template.json) - plantilla / template.
- [Inventario de componentes / Component inventory](component-inventory.json).
- [Huella del paquete / Package file hashes](asset-manifest.json).
- [Referencia de la versión / Release baseline](release-baseline.json).
- [Declaración de autoría / Ownership declaration](templates/OWNERSHIP_DECLARATION_DRAFT.md).
- [Confirmación de compra / Order confirmation](templates/ORDER_CONFIRMATION_DRAFT.md).
- [Acta de aceptación / Acceptance record](templates/ACCEPTANCE_RECORD.md).
- [Registro de incidente / Incident record](templates/INCIDENT_RECORD.md).

## ES / EN - Estado de publicación / Publication state

**P - No aprobado para publicación comercial / Not approved for commercial release.**
Faltan datos del vendedor, decisiones de licencia/soporte, revisión de derechos,
firma comercial y aceptación manual. / Publisher data, licence/support decisions,
rights review, commercial signing and manual acceptance remain open.

Los originales de licencias se conservan sin traducir; las explicaciones son
bilingües. Las fuentes Markdown y JSON son editables; el PDF es una copia de
revisión. / Original licences remain untranslated; explanations are bilingual.
Markdown/JSON sources are editable; the PDF is a review copy.

## ES / EN - Regenerar el PDF / Rebuild the PDF

Desde la raíz del repositorio, usar Python con ReportLab instalado en el entorno
de autoría. No es una dependencia de Cauces ni requiere red durante la generación.
El script usa por defecto Arial y Courier New de macOS; `--font-dir` permite
indicar una carpeta con esos mismos archivos. / From the repository root, use
Python with ReportLab in the authoring environment. Cauces does not depend on it,
and generation is offline. The script defaults to macOS Arial and Courier New;
`--font-dir` selects a directory containing the same font files.

```sh
python3 docs/commercial/tools/build_dossier.py \
  --output dist/Cauces-Commercial-Documentation-0.4.2-ES-EN.pdf
```

El PDF contiene los 19 documentos Markdown. Los inventarios JSON y los textos
íntegros de licencias se entregan como archivos separados en el ZIP; no deben
sustituirse por el resumen del PDF. / The PDF includes the 19 Markdown documents.
JSON inventories and complete original licences are separate files in the ZIP;
the PDF summary does not replace them.
