# `tests/` — verificación formal (el gate)

Pruebas con **pytest** que demuestran que algo funciona **antes** de darlo por bueno.

- **Sí se versiona.** Es la puerta entre el tanteo (`sandbox/`) y el entregable (`output/`).
- Todo bug corregido lleva un test que lo **reproduce antes del fix**; cubrir happy path + edge + caso vacío.
