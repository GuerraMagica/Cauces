# Prueba Windows x64 — pendiente de ejecución

Ejecutables compilados con MinGW para Windows x64, ONNX Runtime CPU 1.31.1 y
los mismos DSP/pipeline que Cauces. No se han ejecutado en Windows ni Wine.
Este kit es local, experimental y no es una versión de Cauces distribuible.
No contiene modelos/pesos; no autoriza su redistribución.

## Requisitos para la prueba futura

- Windows 11 x64, Python 3 con launcher `py` (solo para el verificador).
- Microsoft Visual C++ Redistributable x64 requerido por el runtime oficial.
- Copia local autorizada de `separator.onnx`, `refiner.onnx`, `weights.bin`.
- Carpeta local no sincronizada. No usar material de producción ni voces reales.

## Ejecución

Abrir PowerShell en esta carpeta. Sin cambiar ExecutionPolicy ni protecciones:

```powershell
.\Run-Probe.ps1 -ModelDirectory 'C:\ruta\local\modelos'
```

Si la política local impide ejecutar scripts, ejecutar manualmente los mismos
comandos que contiene el PS1, sin modificar la política. El script no instala
Python, runtimes ni herramientas. No necesita red.

Recorre los contratos del motor/API, nueve fixtures sintéticos y 27 exportaciones,
BWF de 64 bits, protección contra sobrescritura y rechazo de un modelo alterado.
Compara con la referencia Mac usando atol=1e-5 y rtol=1e-4. Cada ejecución crea
un directorio nuevo `results/windows-x64-<fecha>`. Un resultado FAIL se conserva.

La aceptación requiere leer los reportes, comprobar dependencias y repetir en
el equipo Windows real. No se han validado MSVC, ARM64, rutas Unicode, drivers,
reproducción, GUI, aislamiento de red, temporales de producción ni proyectos
largos. Los adaptadores de archivo son experimentales y requieren revisión y
pruebas específicas antes de integrarlos en la aplicación.
