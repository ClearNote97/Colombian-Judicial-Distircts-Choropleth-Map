# 📓 Bitácora de decisiones

> **Fuente única de verdad** de las decisiones de diseño no triviales del proyecto
> (ver [`../README_AGENTS.md`](../README_AGENTS.md) §7). La memoria del agente **apunta aquí**, no guarda copia aparte.
>
> **Cómo se usa:** una entrada por decisión, en orden cronológico (la más antigua primero). Cada decisión
> tiene un ID `D-NNN` que **no se reutiliza**. Si una decisión reemplaza o revierte a otra, se enlazan por
> su ID y se actualiza el **estado** de ambas. El índice permite escanear sin leer todo.

## Índice

| ID | Decisión | Fecha | Estado |
|---|---|---|---|
| [D-001](#d-001--refactorización-a-la-plantilla-clearnote_py_da) | Refactorización a la plantilla ClearNote_Py_DA (conservando historial) | 2026-10-04 | Aceptada |
| [D-002](#d-002--python-3145-y-estrategia-de-build-del-stack-geoespacial) | Python 3.14.5 + estrategia de build del stack geoespacial | 2026-10-04 | Aceptada |
| [D-003](#d-003--de-notebook-monolítico-a-pipeline-de-scripts) | De notebook monolítico a pipeline de scripts; producto = mapas multinivel | 2026-10-04 | Aceptada |
| [D-004](#d-004--homologación-municipio--código-dane-por-nombre-no-por-número-del-pdf) | Homologación municipio → código DANE por nombre normalizado + override YAML | 2026-10-04 | Aceptada |
| [D-005](#d-005--fuente-de-geometría-dane-mgn) | Fuente de geometría: shapefile oficial DANE/MGN | 2026-10-04 | Aceptada |
| [D-006](#d-006--producto-judicial-céntrico-el-departamento-no-es-nivel-de-salida) | Producto judicial-céntrico; el departamento no es nivel de salida | 2026-10-04 | Aceptada · refina D-003/D-004 |
| [D-007](#d-007--viz-en-matplotlib-pngpdf-no-plotly) | Viz en matplotlib (PNG/PDF), no plotly | 2026-10-06 | Aceptada · reemplaza viz plotly |

---

## D-001 — Refactorización a la plantilla ClearNote_Py_DA

- **Fecha:** 2026-10-04
- **Estado:** Aceptada
- **Contexto:** El proyecto nació como un único notebook de ~15 MB (primer proyecto del autor). Se quiere un entorno reproducible y portable (Dev Containers), y una estructura profesional.
- **Decisión:** Adoptar la plantilla `ClearNote_Py_DA` (Dev Container + `uv` + estructura `sandbox/→tests/→output/`) **sobre el repo actual, conservando el historial git** (sin `rm .git`). La versión original se preserva intacta en `docs/legado/`.
- **Por qué:** Reproducibilidad, un solo comando de arranque (`Reopen in Container`), y respeto por el legado (valor personal e histórico).
- **Alternativas descartadas:** Empezar un repo nuevo (`rm .git`) — se perdería la historia del primer proyecto del autor.
- **Consecuencias:** El `README.md` raíz se reescribe desde cero; el legado queda como referencia no ejecutable.

## D-002 — Python 3.14.5 y estrategia de build del stack geoespacial

- **Fecha:** 2026-10-04
- **Estado:** Aceptada
- **Contexto:** La plantilla trae `python:3.14.5-slim-bookworm`. El proyecto usa un stack geoespacial pesado (`geopandas`, `fiona`/`pyogrio`, `shapely`, `pyproj`) + `camelot-py` (que necesita Ghostscript) + `opencv`. Riesgo: que no existan wheels para 3.14 y el container falle al construir.
- **Decisión:** Mantener **Python 3.14.5** (elección del autor) y endurecer el `Dockerfile` con Ghostscript + libs de sistema de respaldo (`gdal-bin`, `libgdal-dev`, `libgeos-dev`, `libproj-dev`, `libglib2.0-0`) para compilar desde fuente si faltaran wheels.
- **Por qué:** Verificación empírica: se construyó la imagen y se replicó el `postCreateCommand` (`uv add -r requirements.txt`) → **todos los imports OK en 3.14.5** sin compilar de fuente (había wheels: pandas 3.0.6, geopandas 1.2.0, shapely 2.1.2, pyproj 3.8.0, pyogrio 0.13.0, camelot 2.0.0, plotly 7.1.0, opencv, Ghostscript 10.00.0 / GDAL 3.6.2).
- **Alternativas descartadas:** Fijar 3.12/3.11 por seguridad — innecesario al confirmarse wheels para 3.14.
- **Consecuencias:** Versiones nuevas con cambios de API a tener en cuenta en la re-implementación: `plotly.Choroplethmapbox` está deprecado (migrar a `Choroplethmap`/MapLibre); `camelot 2.0` y `pandas 3.0` pueden diferir de la era del notebook.

## D-003 — De notebook monolítico a pipeline de scripts

- **Fecha:** 2026-10-04
- **Estado:** Aceptada
- **Contexto:** El autor ya no quiere trabajar en notebooks sino con scripts profesionales ejecutables con un solo comando.
- **Decisión:** Re-implementar el pipeline como paquete en `src/judicial_map/` ejecutable con un comando (p. ej. `uv run python -m judicial_map`). `notebooks/` queda solo para exploración. El **producto principal** son los **archivos de mapa a distintos niveles** (municipio/circuito/distrito/departamento) en formatos importables (geojson/json/xlsx) para Power BI, Dash, etc., en `output/`. Los `.xlsx` de eficiencia (DB1/DB2) son **datos de ejemplo** para verificar el pipeline (el gate), no el producto.
- **Por qué:** Mantenibilidad, reproducibilidad y reutilización de las salidas en otras herramientas.
- **Alternativas descartadas:** Mantener el flujo en notebook — frágil, no testeable, no "un comando".
- **Consecuencias:** Hay que definir la frontera de módulos (`ingest`/`clean`/`merge`/`export`/`viz`) y la homologación de nombres (ver D-004).

## D-004 — Homologación municipio → código DANE por nombre (no por número del PDF)

- **Fecha:** 2026-10-04
- **Estado:** Aceptada
- **Contexto:** El notebook legado homologaba los nombres de municipio con ~400 correcciones regex frágiles. Hipótesis del autor: el "No." de municipio del PDF equivale a las últimas 3 cifras del código DANE (`mmm`), lo que permitiría construir el código sin cruzar nombres.
- **Decisión:** Homologar `municipio del PDF → código DANE` por **nombre normalizado + reglas sistemáticas + desambiguación por *footprint* del distrito + override YAML** para el residuo. El *footprint* (departamentos donde caen los municipios ya resueltos de un distrito) se **deriva de los datos**, no de una tabla impuesta (ver D-006).
- **Por qué:** Se verificó empíricamente la hipótesis del número del PDF y **NO se sostiene**: sobre 689 municipios que matchean DANE por nombre, solo el **2.3%** cumple `nº_PDF == mmm`; el número del PDF va de 1 a 20 (es un ordinal por circuito, no el código DANE, que llega a ~900). Prueba indirecta: la existencia misma de las 400 correcciones en el legado implica que el cruce siempre fue por nombre. Medición del cruce por nombre: 87% solo-normalización → 91% con reglas (PTO→PUERTO, STA→SANTA, quitar sufijo `(DEPTO)`); residuo ~94 (typos como `ZRAZAL`, renombres oficiales como `MOMPOX`). 67 nombres son ambiguos entre departamentos → el scoping por departamento (gratis vía distrito) los desambigua.
- **Núcleo válido del insight del autor:** las últimas 3 cifras SÍ son el código de municipio dentro del departamento, y el **código DANE es la llave de unión** DIVIPOLA ↔ geometría (por eso se necesitaba "para las coordenadas"). Lo que no aplica es leerlo del PDF; se **construye**.
- **Alternativas descartadas:** (a) Código directo del número del PDF — refutado por los datos. (b) 400 regex como el legado — frágil, no trazable. (c) Dicts en código — menos editable que YAML.
- **Consecuencias:** El módulo `homologate`: `override → nombre único → footprint → (residuo) override`. **Resultado verificado:** cobertura **1104/1104** (865 `unique`, 135 `footprint`, 104 `override`), 0 sin resolver, 0 códigos inválidos. El `override_municipios.yaml` tiene 104 entradas keyed por `distrito :: municipio`. Se detectaron y corrigieron **5 "nombre único equivocado"** (SANTUARIO→El Santuario 05697, PUEBLO RICO→Pueblorrico 05576, EL PEÑOL→Peñol 05541, EL CARMEN→El Carmen de Chucurí 68235, MANAURE→Manaure Balcón del Cesar 20443) vía chequeo de duplicados + footprint. Quedan 2 duplicados **intencionales** (corregimientos que comparten polígono): Santa Rita→Cumaribo (99773) y Coconuco→Puracé (19585).

## D-005 — Fuente de geometría: DANE/MGN

- **Fecha:** 2026-10-04
- **Estado:** Aceptada
- **Contexto:** La fuente de geometrías municipales del legado (bogota-laburbano opendatasoft) ahora responde **403 Forbidden** — murió.
- **Decisión:** Reemplazarla por el **shapefile oficial del DANE (Marco Geoestadístico Nacional, MGN)**, que trae geometrías municipales con código DANE. Se cachea en `data/other/cache/` para reproducibilidad.
- **Por qué:** Fuente autoritativa y estable; el código DANE incluido permite unir por clave (D-004) sin nombres.
- **Alternativas descartadas:** Mantener la fuente muerta (imposible); buscar otro portal no-oficial (menos confiable).
- **Consecuencias:** Verificar acceso/URL del MGN al implementar `ingest`; definir estrategia de caché de un archivo grande.

## D-006 — Producto judicial-céntrico; el departamento no es nivel de salida

- **Fecha:** 2026-10-04
- **Estado:** Aceptada (refina D-003 y D-004)
- **Contexto:** El valor de investigación del proyecto es mostrar que **la geografía judicial NO coincide** con la división político-administrativa. Enmarcar la salida por departamento contradice el propósito.
- **Decisión:** Los niveles de salida son **judiciales**: `municipio → circuito → distrito`. El departamento **no es** un nivel de salida. DIVIPOLA/geometría son **instrumentales** (código DANE → geometría) para luego agregar por unidad judicial. **No se crea un artefacto distrito→departamento**; la desambiguación usa el *footprint* derivado de los datos.
- **Por qué:** Petición explícita del autor; el cruce con lo político-administrativo solo sirve para dar geometría y agregar, no para describir el territorio judicial.
- **Hallazgos que valida (ver `docs/hallazgos-geograficos.md`):** 12 municipios cuyo distrito judicial está en otro departamento (el PDF los marca con `(BOY)`, `(CESAR)`, etc.); Villavicencio abarca 6 departamentos; varios departamentos tienen 2 distritos judiciales.
- **Consecuencias:** `config.LEVELS = ("municipio", "circuito", "distrito")`. El `dissolve` final es por columna judicial, no por departamento.

## D-007 — Viz en matplotlib (PNG/PDF), no plotly

- **Fecha:** 2026-10-06
- **Estado:** Aceptada (reemplaza la viz en plotly)
- **Contexto:** Los mapas de ejemplo se hicieron primero en Plotly (HTML interactivo). Al agregar la figura completa del país como base, el mapa salía **en blanco** en el navegador.
- **Decisión:** Hacer los mapas en **matplotlib** (salida **PNG + PDF** estática), no Plotly. Se quitaron `plotly` y `kaleido` de las dependencias; se agregó `matplotlib`.
- **Por qué:** Se aisló la causa con render real: **plotly.js no renderiza las geometrías de las áreas no municipalizadas de la Amazonía** (16 de los 20 municipios sin juzgado) — deja toda la figura en blanco, aun disueltas/simplificadas a un solo polígono. matplotlib las dibuja sin problema, y PNG/PDF de alta calidad sirven mejor para publicaciones.
- **Alternativas descartadas:** Contorno nacional limpio de fuente externa (geoBoundaries ADM0, 707 coords) — también falló en plotly.js: el problema es el motor, no la geometría de origen.
- **Consecuencias:** Mapas estáticos (sin hover/zoom). El inset de San Andrés usa transformación afín (escala + acerca Providencia, **no a escala real**) para legibilidad. El producto (geojson/xlsx) queda intacto.

---

<!-- ─────────────────────────────────────────────────────────────────────────────
PLANTILLA PARA UNA NUEVA DECISIÓN
(copia el bloque de abajo, quítale los comentarios, asígnale el número de ID y
agrégalo también a la tabla del Índice de arriba)

## D-NNN — <título corto de la decisión>

- **Fecha:** AAAA-MM-DD
- **Estado:** Aceptada          <!-- Aceptada | Reemplaza a D-XXX | Reemplazada por D-YYY | Revertida -->
- **Contexto:** <qué problema o disyuntiva la motivó>
- **Decisión:** <qué se decidió, en una frase>
- **Por qué:** <la razón principal y los criterios considerados>
- **Alternativas descartadas:** <qué otras opciones se evaluaron y por qué no>
- **Consecuencias:** <qué implica, a favor y en contra>

───────────────────────────────────────────────────────────────────────────── -->
