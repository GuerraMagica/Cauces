# Cauces — refuerzo de regresiones de infraestructura

Alcance aprobado en el chat el 01-11-2026. Ejecutar inline con
superpowers:executing-plans, test-driven-development y verificación final.
No hay spec separada: el alcance aprobado del chat es la referencia.

## Objetivo y límites

- Crear y subir primero el respaldo del estado 0.4.1, preservando cambios
  locales y remotos; registrar la autorización permanente de commit/push.
- Cubrir protocolo e integridad en ARM64 y x86_64/Rosetta; transporte Swift
  contra el worker de cada arquitectura.
- Aislar alteración, ausencia y FIFO de cada asset usado por el worker/API C.
- Cubrir FIFO como fuente en el inspector y hash del worker.
- No modificar código de producción, pesos, DSP, proveedor o Settings.
- No atribuir mejoras de audio a estas pruebas. La escucha sigue pendiente.

## Pasos y aceptación

1. Respaldo: suite actual, revisión de archivos/secretos, commit y push; verificar
   SHA remoto. Conservar el cambio remoto de Model-NOTICE.txt.
2. Harness: parametrizar arquitectura sin instalar dependencias. Cada test debe
   verificar qué arquitectura ejecuta realmente. Los probes API deben tener
   timeout externo para detectar FIFO bloqueante sin colgar la suite.
3. Integridad: controles positivos con assets propios aprobados; después alterar
   un solo asset, eliminarlo o sustituirlo por FIFO y exigir rechazo de integridad
   en API/worker. Comprobar hashes/mtime originales al terminar. Sin inferencia
   sobre modelos no aprobados ni descargas.
4. Validación: ejecutar la suite completa, tests de paquete y probes sandbox del
   paquete conservado en ambas arquitecturas. Sin cambiar dispositivos de audio.
   Revisar el diff completo y documentar límites; commit/push y SHA remoto.

## Registro

- Respaldo previo: 59bdd29; suite existente completa PASS. Main remoto tenía
  2da9da0 (atribución): incorporado mediante fast-forward sin descartar cambios.
- Decisión: ampliar pruebas de comportamiento existente; no hay fallo de producto
  nuevo que corregir. No se modificará producción para forzar un RED artificial.
- Preflight: protocolo e integridad comparten selector DS_TEST_ARCH; transporte
  Swift utiliza target y worker concordantes. Artefactos de prueba bajo build/.
- Harness implementado: DS_TEST_ARCH para protocolo/integridad; API en proceso
  aislado con arquitectura comprobada y timeout externo. Transporte Swift con
  target y worker concordantes en ambas arquitecturas.
- Integridad: 36 rechazos individuales (tres assets × tres fallos × dos entry
  points × dos arquitecturas), controles válidos antes/después y originales
  intactos. FIFO de fuente rechazado por inspector/hash, con recuperación.
- Suite ampliada PASS: 8/8 CTest por arquitectura, Swift/protocolo/integridad,
  WAV adversariales y exportación. Probes App Sandbox y paquete/ZIP reubicado
  PASS; 44100 Hz/352800 muestras, red EPERM en padre/hijo. Sin cambios de producto.
- Revisión final independiente: sin hallazgos Critical/Important/Minor. Se
  revisaron código, alcance y logs; el revisor no volvió a ejecutar las suites.
- Ruling final: los probes sustituyen el entry point GUI y no prueban concesiones
  NSOpenPanel; Rosetta no valida Intel físico; señales sintéticas no acreditan
  calidad auditiva. Son límites conocidos, no cambios pendientes de este alcance.
- Publicación: commit del refuerzo en origin/codex/cauces-ui-design; identificar
  su SHA definitivo y la comprobación remota en la respuesta de entrega.
