# Fuentes de Cauces / Cauces source information

El código, scripts, pruebas, documentación y artwork propios están bajo
GPL-3.0-only; los modelos y componentes de terceros conservan su ámbito separado.
Consultar COPYRIGHT, LICENSE_SCOPE.md y los textos completos de esta carpeta.

Fuentes del proyecto: https://github.com/GuerraMagica/Cauces
La entrega local de build 7 incluye un archivo de fuentes propias identificado
por commit y una colección separada de fuentes de terceros. El manifiesto de
entrega relaciona sus hashes con el ZIP de la app. Las instrucciones de
compilación y obtención de dependencias están en README.md y RELEASE.md.
No se incluyen grabaciones, modelos o pesos en el archivo de fuentes propias.

Original code, scripts, tests, docs and artwork are GPL-3.0-only. Third-party
components and models retain their separate terms. The local build 7 delivery
pairs an application ZIP with a commit-identified project-source archive and
separate third-party sources, linked by checksums in its release manifest.
Build/dependency instructions are in README.md and RELEASE.md.

Runtime source identities differ by architecture; use dependency-inventory.json:
ARM64 official binary: 41d4d61f14b9c1dd0b2ccda1e9b85dd415fd0496.
Intel source build: 6af1a932e2286d5c58166085d24c68783033edee.
The ARM64 vendor binary has no supplied per-component SBOM/build cache. Its
upstream pin/notice inventory is a conservative superset, not a certification of
binary inclusion. Full original runtime notices are retained. Pinned third-party
sources and download/build recipes are provided; byte-identical regeneration of
the official ARM64 runtime is not claimed.

JSON 3.11.3 headers match the pinned source tree. The root licence and additional
header copyright notices are both retained, including incorporated helper code.
The runtime's licence does not license the model assets it executes.

Public redistribution of the complete candidate remains pending model rights.
The local package is ad hoc signed, not Developer ID signed or notarized.
