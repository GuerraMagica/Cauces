# Cauces — instrucciones de trabajo

Estas instrucciones complementan las instrucciones personales del usuario.

## Versionado autorizado

- Tras cada conjunto coherente de cambios autorizados, revisa el diff, ejecuta
  las comprobaciones pertinentes, crea un commit y haz push a `origin` en la
  rama de trabajo aprobada. El usuario ha autorizado este flujo de forma
  continuada; no vuelvas a pedir permiso para cada commit/push ordinario.
- Comprueba que el SHA de la rama remota coincide con el commit local e informa
  de los commits de respaldo y de los cambios entregados. Un commit local sin
  push no cuenta como respaldo en GitHub. Si falla el acceso, informa sin
  afirmar que está subido ni intentar eludir permisos.
- Conserva los cambios preexistentes y remotos. No uses force push, reset hard,
  clean ni sobrescribas trabajo ajeno. No publiques en `public-archive`.
- Añade archivos explícitamente y revisa secretos/datos privados antes de subir.
  Audio, modelos, pesos, paquetes, entornos y evidencia privada permanecen
  locales y excluidos por `.gitignore`; conserva los artefactos necesarios para
  reproducir una versión localmente. GitHub no es un respaldo de esos archivos.
- Los planes históricos pueden registrar aprobaciones antiguas que excluían
  commits; no anulan la autorización de versionado posterior del usuario.

## Frontera del producto

- Cauces y MULTI SPEAKER SEPARATION LAB son proyectos independientes.
- No traslades modelos, pesos o DSP del LAB para corregir infraestructura.
- Preserva acting, timbre, respiraciones, consonantes, alineación y el contrato
  de metadata. Distingue validación sintética de escucha profesional.
- Mantén el procesamiento local y App Sandbox sin permisos de red.
