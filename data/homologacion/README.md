# `data/homologacion/` — tablas de homologación municipio → código DANE

Reemplazan las ~400 correcciones regex del notebook legado por tablas versionadas y trazables.

- **`override_municipios.yaml`** — residuo que no resuelve el match por nombre único ni por
  *footprint* del distrito. Clave `"DISTRITO :: MUNICIPIO (grafía PDF)"` → código DANE, curado y
  verificado contra DIVIPOLA. Incluye correcciones de "nombre único equivocado" y decisiones de
  dominio (corregimientos: Santa Rita→Cumaribo, Coconuco→Puracé).

El resto de la homologación (normalización + reglas + footprint) es código en
`src/judicial_map/homologate.py`. Diseño y evidencia: `docs/bitacora-decisiones.md` (D-004).
