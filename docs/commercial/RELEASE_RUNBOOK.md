# Publicación y firma / Release and signing runbook

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## ES - Estado y responsabilidades

Procedimiento futuro, NO ejecutado por crear este dossier. 0.4.2 es una beta
personal ad hoc. Elegir versión comercial, vendedor, canal y responsable de firma;
no sobrescribir dist ni publicar la beta personal como ya notarizada. Crear una
copia separada y conservar la referencia inmutable. El ID actual es
local.julio.cauces: confirmar identificador estable y migración de preferencias
si se decide cambiarlo. No hacerlo silenciosamente.

Antes de firmar: cerrar decisiones y derechos de LICENSES_PROVENANCE/LEGAL_REVIEW,
completar textos de clientes, verificar la etiqueta v1 en el futuro paquete y
ejecutar VALIDATION_PLAN. El aviso histórico v3 se conserva; ver LICENSES_PROVENANCE.
Confirmar que el empaquetador real añade los textos/avisos aprobados; este dossier
NO los ha insertado en la app 0.4.2. Mantener todos los hashes de modelo fijados.

## EN - Status and responsibilities

Future procedure, NOT executed by creating this dossier. Version 0.4.2 is an ad
hoc personal beta. Select commercial version, seller, channel and signing owner;
do not overwrite dist or describe that beta as notarized. Work on a separate copy
and keep an immutable reference. Current ID is local.julio.cauces: confirm a stable
identifier and preference migration if changing it; do not silently replace it.

Before signing, resolve LICENSES_PROVENANCE/LEGAL_REVIEW, complete customer texts,
verify the v1 label in the future package and run VALIDATION_PLAN. Retain the
historical v3 notice; see LICENSES_PROVENANCE. Confirm actual packaging includes
approved notices/documents: this dossier has NOT inserted them into app 0.4.2.
Retain pinned model hashes.

## ES - Preparación y secuencia técnica

Usar Apple Developer ID autorizado, claves en llavero, perfiles de notarytool y
credenciales fuera de Git/logs. La firma comercial/servicio Apple y su posible
coste requieren decisión del titular; no se crean cuentas ni se sube software aquí.
El envío a notarización comparte el paquete con Apple, aunque Cauces siga offline.
Revisar la excepción de library validation del worker: con todas las librerías
firmadas por el mismo equipo puede evaluarse su retirada, pero cualquier cambio
requiere autorización y repetir pruebas, no una edición automática de seguridad.

## EN - Preparation and technical sequence

Use authorised Apple Developer ID, Keychain-held keys and notarytool profiles;
keep credentials out of Git/logs. Commercial signing/Apple submission and any
cost require owner decisions; no account or upload is made here. Notarization
shares the package with Apple even though runtime audio stays offline. Review
the worker's library-validation exception: same-team signing may allow removal,
but changes require approval and retesting, not automatic security edits.

## ES / EN - Secuencia de ejemplo / Example sequence

Ejecutar solo con valores revisados y destinos nuevos. / Run only with reviewed
values and new output paths. No passwords or private keys belong in these commands.

```sh
# Preparar variables propias / Set task-specific variables
CAUCES_INPUT_APP='path/to/personal-reference/Cauces.app'
CAUCES_SIGNED_APP='path/to/new-release/Cauces.app'
CAUCES_DEVELOPER_ID='Developer ID Application: LEGAL NAME (TEAMID)'
CAUCES_NOTARY_PROFILE='EXISTING_KEYCHAIN_PROFILE'
CAUCES_NOTARY_ZIP='path/to/new-release/notary-submission.zip'
CAUCES_NOTARY_REPORT='path/to/new-release/notary-report.json'

# Copia nueva; comprobar que el destino no existe / Require new destination
test ! -e "$CAUCES_SIGNED_APP" || exit 1
test ! -e "$CAUCES_NOTARY_ZIP" || exit 1
test ! -e "$CAUCES_NOTARY_REPORT" || exit 1
ditto "$CAUCES_INPUT_APP" "$CAUCES_SIGNED_APP" || exit 1
for CAUCES_LIB in "$CAUCES_SIGNED_APP"/Contents/Frameworks/*.dylib; do
  codesign --force --sign "$CAUCES_DEVELOPER_ID" --timestamp \
    "$CAUCES_LIB" || exit 1
done
codesign --force --sign "$CAUCES_DEVELOPER_ID" --timestamp \
  --options runtime --entitlements resources/Worker.entitlements \
  "$CAUCES_SIGNED_APP/Contents/MacOS/dialogue-worker" || exit 1
codesign --force --sign "$CAUCES_DEVELOPER_ID" --timestamp \
  --options runtime --entitlements resources/Cauces.entitlements \
  "$CAUCES_SIGNED_APP" || exit 1
codesign --verify --deep --strict --verbose=2 "$CAUCES_SIGNED_APP" || exit 1
ditto -c -k --sequesterRsrc --keepParent \
  "$CAUCES_SIGNED_APP" "$CAUCES_NOTARY_ZIP" || exit 1
xcrun notarytool submit "$CAUCES_NOTARY_ZIP" \
  --keychain-profile "$CAUCES_NOTARY_PROFILE" --wait \
  --output-format json > "$CAUCES_NOTARY_REPORT" || exit 1
# Exigir estado Accepted / Require Accepted
test "$(plutil -extract status raw -o - \
  "$CAUCES_NOTARY_REPORT")" = Accepted || exit 1
xcrun stapler staple "$CAUCES_SIGNED_APP" || exit 1
xcrun stapler validate "$CAUCES_SIGNED_APP" || exit 1
spctl --assess --type execute --verbose=4 "$CAUCES_SIGNED_APP" || exit 1
```

## ES - Cierre de publicación

Crear el ZIP final DESPUÉS de stapling; verificar su extracción, firma y hashes,
los modelos contra el manifest, ausencia de rutas al build y ambos slices. La
firma nueva cambia hashes de ejecutables y ZIP: emitir una referencia nueva, no
copiar el checksum 0.4.2. Probar descarga real con Gatekeeper y conservar logs
Accepted/ticket/actas sin credenciales. Publicar por un canal autenticado con
checksums/notas/condiciones, sin reportar conexión inexistente desde la app.

Registrar responsable y aprobación comercial, commit, firma Team ID, OS/driver,
fecha, destino y procedimiento de retirada. Ante un incidente, suspender entrega
si procede, preparar corrección firmada y conservar una versión anterior conocida.
No forzar resets en Git ni borrar exportaciones del usuario. Fuentes S9 de SOURCES.

## EN - Publication closeout

Create the final ZIP AFTER stapling; verify extraction, signatures, model hashes,
relative dependencies and both slices. Re-signing changes executable/ZIP hashes:
issue a new reference rather than reusing the 0.4.2 checksum. Test an actual
download under Gatekeeper and retain Accepted/ticket/acceptance records without
credentials. Publish through an authenticated channel with checksums, notes and
terms; do not claim the app makes an update connection it does not have.

Record owner approval, commit, Team ID, tested OS/driver, date, destination and
withdrawal procedure. Where appropriate, suspend delivery, ship a signed fix and
retain a known earlier release. Do not force-reset Git or delete user exports.
See S9 in SOURCES.
