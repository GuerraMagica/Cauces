# Mantenimiento y traspaso / Maintenance and handover

Versión documental / Document revision: 1.0 | 2026-11-02 | Cauces 0.4.2, build 6

## ES - Inventario y reconstrucción

La base documentada es commit 33dc57ad10d00ca8e94c8046fb0537db5d11d193,
Cauces 0.4.2 build 6. El commit de documentación posterior no cambia esa app.
GitHub conserva código, pruebas, diseño y documentación en la rama de trabajo;
no conserva audio, pesos, vendor, build, evidencias ni ZIP. No asumir que clonar
el repositorio recupera el producto completo. El LAB es independiente.

Custodiar en almacenamiento controlado el ZIP 0.4.2/checksum, modelos exactos,
manifest, fuentes fijadas de ORT, avisos y evidencias de procedencia/conversión
disponibles. Conservar además evidencias de aceptación autorizadas sin añadir voces privadas
a Git. Guardar claves de firma en custodia separada; un hash no reemplaza backup.

Para reconstruir, usar macOS y herramientas Apple, CMake/Ninja existentes o una
preparación aprobada. scripts/prepare-runtime.sh necesita red y obtiene fuentes
fijadas; revisar descargas/licencias antes de ejecutarlo. scripts/build.sh produce
ARM/x86; scripts/package.sh genera un destino NUEVO y firma ad hoc, no Developer ID.
Definir CAUCES_MODEL_DIR y CAUCES_PACKAGE_PATH sin sobrescribir originales.
Después ejecutar tests/run_security_tests.sh, tests/package_test.py y los probes
sandbox por arquitectura; ver RELEASE_RUNBOOK para la distribución comercial.

## EN - Inventory and reconstruction

Documented baseline: commit 33dc57ad10d00ca8e94c8046fb0537db5d11d193,
Cauces 0.4.2 build 6. The later documentation commit does not change that app.
GitHub holds source/tests/design/docs on the working branch, not audio, weights,
vendor/build, evidence or ZIPs. A clone is not a complete product backup. LAB is
independent.

Keep the 0.4.2 ZIP/checksum, exact models, manifest, pinned ORT sources, notices
and available provenance/conversion evidence in controlled storage. Keep authorised
acceptance evidence without committing private voices. Signing keys need separate custody;
a checksum is not a backup.

Rebuild with macOS/Apple tools and existing or approved CMake/Ninja setup.
scripts/prepare-runtime.sh accesses the network for pinned sources; review
licences/downloads first. scripts/build.sh builds ARM/x86; scripts/package.sh
requires a NEW destination and signs ad hoc, not Developer ID. Set CAUCES_MODEL_DIR
and CAUCES_PACKAGE_PATH without overwriting originals. Run security suites,
package tests and architecture-specific sandbox probes, then RELEASE_RUNBOOK.

## ES - Cambios futuros y entrega

Antes de editar: Git/instrucciones/diff; snapshot lógico y preservar trabajo ajeno.
Tras cada cambio autorizado coherente: comprobar, commit, push a origin/rama
aprobada y verificar SHA remoto según AGENTS. No usar public-archive ni force push.
Versionar formato/metadata/compatibilidad explícitamente. No trasladar modelos
ni DSP del LAB para corregir infraestructura.

Actualizar matriz, licencias, inventario, hashes, notas, manual y condiciones
cuando cambien. No elevar cifras sintéticas a garantías perceptivas. Una petición
de soporte no autoriza material audiovisual externo, nuevas cuentas o compras.
El equipo entrante recibe permisos mínimos de repositorio, custodia de assets y
responsables comerciales; este documento no concede accesos por sí mismo.

## EN - Future changes and handover

Inspect Git/instructions/diff and preserve other work before editing. After each
coherent authorised change, verify, commit, push to the approved origin/branch and
confirm remote SHA per AGENTS. No public-archive or force push. Version audio,
metadata and compatibility contracts explicitly. Do not transfer LAB models/DSP
to solve infrastructure issues.

Update the matrix, licences, inventory, hashes, notes, manual and terms as things
change. Synthetic metrics are not perceptual guarantees. Support requests do not
authorise external audiovisual sharing, new accounts or spending. A receiving
team needs least-privilege repository/asset custody and named business owners;
this document itself grants no access.
