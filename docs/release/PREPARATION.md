# Preparación técnica de Cauces 0.4.2 build 7

Alcance aprobado el 04-11-2026: revisar dependencias/avisos, corregir empaquetado,
compilar desde fuentes limpias, ejecutar pruebas del candidato, preparar fuentes,
ZIP/checksums/notas y prueba de descarga, con commit/push en la rama de trabajo.

Referencia funcional inmutable: 0.4.2 build 6. El nuevo build 7 identifica cambios
exclusivamente de distribución; no cambia DSP, modelos, pesos ni entitlements.
Se reutiliza el checkout aprobado `codex/cauces-ui-design`, limpio al comenzar.
Los artefactos con modelos y las evidencias permanecen locales; el código y la
información pública de dependencias se respaldan en GitHub. No se fusiona main.

## Plan y criterios de aceptación

- [x] Revisar los dos runtimes por separado: commit real, providers disponibles,
  dependencias fijadas y avisos íntegros. Reconciliar el árbol JSON 3.11.3 y sus
  atribuciones internas. No confundir el inventario upstream con prueba de enlace.
- [x] Probar primero el contrato de licencias del paquete; añadir GPL, alcance,
  Apache, avisos y procedencia de fuentes. Rechazar entradas ausentes/alteradas.
- [x] Exportar fuentes revisadas a una carpeta limpia; copiar solo dependencias
  de compilación fijadas; compilar ARM64/x86_64. Ejecutar pruebas públicas e
  integración con fixtures sintéticos y assets locales autorizados.
- [x] Empaquetar en destino nuevo y comprobar arquitecturas, firmas ad hoc,
  ausencia de red, modelos, licencias, exportación y extracción en otro destino.
- [x] Generar fuentes propias y fuentes de terceros identificadas, ZIP, manifiesto
  y SHA-256. Probar transferencia local del candidato y descarga pública de las
  fuentes después del push; no subir modelos ni presentar la prueba local como
  aceptación de Gatekeeper desde Internet.
- [x] Revisión independiente final, commit/push y comparación SHA remoto/local.

## Hallazgos y decisiones

- El runtime ARM64 oficial 1.31.1 identifica el commit
  `41d4d61f14b9c1dd0b2ccda1e9b85dd415fd0496`; el Intel local identifica
  `6af1a932e2286d5c58166085d24c68783033edee`. Ambos declaran 1.31.1.
- ARM64 contiene CoreML, WebGPU y CPU; Intel contiene CPU. Cauces sigue usando CPU.
  Se preservan los binarios de runtime y se registra la granularidad de evidencia.
- La fuente ARM64 exacta se ha obtenido de upstream y sus pins `cmake/deps.txt`
  coinciden con los de Intel. La publicación oficial no aporta un SBOM por binario;
  el inventario distinguirá componentes confirmados, candidatos y herramientas.
- Los headers JSON 3.11.3 contienen atribuciones adicionales a la licencia raíz;
  se conservarán conjuntamente, sin alterar los textos originales.

## Límites de aceptación

La compilación y los controles sintéticos no sustituyen escucha profesional,
Intel físico, Pro Tools o aceptación manual de GUI. La firma sigue siendo ad hoc;
no se dispone de autorización ni credenciales para una notarización nueva.
La revisión del refinador queda pendiente; preparar un ZIP local no autoriza
redistribuir públicamente sus pesos.

## Revisión independiente y correcciones

La revisión detectó dos huecos en la herramienta inicial: insumos de fuentes
registrados al empaquetar sin vincularlos al build, y árboles locales de terceros
sin comprobación de integridad. Se añadieron registros por arquitectura con
insumos antes/después de compilar y hashes de salidas; el empaquetador exige
coincidencia y los hashes ORT revisados. La entrega comprueba el conjunto exacto
de dependencias CPU y sus huellas. Las fuentes ORT proceden del archivo ARM64
upstream con SHA-256 verificado y de git archive del commit Intel fijado.
Los enlaces relativos internos legítimos de upstream se conservan; se rechazan
los enlaces de fuentes absolutos o que escapen del árbol.

## Resultado de la entrega

Fuentes funcionales del candidato: commit `605cc735348238f3f06fc735a6ffe126f8533d70`,
respaldado en GitHub y confirmado por SHA remoto. La actualización posterior de
este registro no cambia las fuentes funcionales ni los archivos de entrega.

Entrega local: `dist/Cauces-0.4.2-build7-delivery/`, con ZIP universal, fuentes
propias, fuentes de terceros, manifiesto, verificación y SHA256SUMS. Checksums y
contenido de los archivos de fuentes verificados: 218 archivos del proyecto,
archivo upstream ARM64 exacto, git archive del commit Intel y los 12 árboles CPU.
Descarga pública real de las fuentes desde GitHub: PASS, 218 archivos idénticos.
Transferencia HTTP de la app exclusivamente en loopback y extracción a destino
nuevo: PASS, 49 archivos del bundle idénticos; firma/dependencias/licencias del
bundle trasladado verificadas. No equivale a probar Gatekeeper desde Internet.

Los binarios completos y las fuentes externas permanecen locales; GitHub recibe
código, avisos y documentación. No se han subido modelos, audio o paquetes, ni se
ha creado una release o fusionado main. La limitación de granularidad del SBOM
ARM64 y las validaciones manuales/derechos pendientes están documentadas.
