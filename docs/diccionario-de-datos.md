# 📖 Diccionario de datos

> Describe **qué significa cada variable** de los datos del proyecto: nombre, tipo, significado, dominio y origen.
> Se organiza **un bloque por dataset** (archivo o tabla) y se llena a medida que se incorporan datos.
>
> **Cómo se usa:** por cada dataset, una breve descripción + una tabla de variables. Copia la plantilla del
> final para agregar un dataset nuevo. Los tipos se escriben en lenguaje llano (`entero`, `decimal`,
> `texto`, `fecha`, `booleano`, `categórico`), no en el tipo interno de pandas.

---

## Producto — `output/mapa_judicial_{municipio,circuito,distrito}.{geojson,topojson,xlsx}`

Archivos de mapa, una fila por unidad judicial. El `.geojson` trae `geometry` (polígono, EPSG:4326);
el `.topojson` trae la misma geometría con topología compartida (para el Shape Map de Power BI,
clave `cod_dane`/`district`); el `.xlsx` trae los mismos atributos sin geometría.

| Variable | Tipo | Descripción | Niveles | Fuente |
|---|---|---|---|---|
| `district` | texto | Distrito judicial (grafía del PDF) | todos | PDF Rama Judicial |
| `circuit` | texto | Circuito judicial | municipio, circuito | PDF Rama Judicial |
| `municipality` | texto | Municipio judicial (grafía del PDF) | municipio | PDF Rama Judicial |
| `cod_dane` | texto (5 díg.) | Código DANE del municipio (`DDMMM`) | municipio | DIVIPOLA (homologado) |
| `municipio_dane` | texto | Nombre oficial del municipio en el MGN | municipio | DANE/MGN |
| `n_municipios` | entero | Municipios agregados en la unidad | circuito, distrito | derivado |
| `geometry` | polígono | Geometría (EPSG:4326), simplificada | todos (solo geojson) | DANE/MGN |

## Jerarquía judicial (intermedio) — `ingest.load_judicial_hierarchy()`

Una fila por municipio judicial, extraída del PDF. Cols: `district`, `circuit`, `municipality`.
~1104 filas · 33 distritos · ~202 circuitos. (El ordinal de municipio del PDF se descarta: es un
ordinal por circuito, no el código DANE — ver `bitacora-decisiones.md` D-004.)

## DIVIPOLA — `data/other/cache/DIVIPOLA_Municipios.xlsx` (hoja `Municipios`)

| Variable | Tipo | Descripción | Fuente |
|---|---|---|---|
| `cod_dane` | texto (5 díg.) | Código municipio `DDMMM` (zero-padded; el Excel lo trae como float) | DANE |
| `cod_depto` | texto (2 díg.) | Código departamento (`cod_dane[:2]`) | DANE |
| `departamento` | texto | Nombre del departamento | DANE |
| `municipio` | texto | Nombre oficial del municipio | DANE |
| `tipo` | categórico | `Municipio` / `Isla` / `Área no municipalizada` | DANE |

## Datos de ejemplo — `data/other/DB1/DB2 *.xlsx`

Eficiencia de juzgados penales por **distrito judicial** (33 filas). Solo para **verificar** el
pipeline (choropleths), no es el producto.

| Variable | Tipo | Descripción | Dominio | Fuente |
|---|---|---|---|---|
| `District` | texto | Distrito judicial (grafía con tildes) | 33 distritos | autor |
| `2012`…`2016` | decimal | Eficiencia anual | `0–1` (puede ser NaN = sin dato) | autor |
| `AVG_Eff` | decimal | Eficiencia promedio del período | `0–1` | autor |

> DB1 = juzgados **municipales**, DB2 = juzgados de **circuito**.

## Homologación — `data/homologacion/override_municipios.yaml`

Residuo de homologación que no resuelve el match por nombre único ni por *footprint*.

| Clave | Valor | Descripción |
|---|---|---|
| `"DISTRITO :: MUNICIPIO"` | texto (5 díg.) | Municipio del PDF (contexto judicial) → código DANE curado |

---

<!-- ─────────────────────────────────────────────────────────────────────────────
PLANTILLA PARA UN NUEVO DATASET (copia este bloque y quítale el comentario)

## `<nombre_del_dataset>` — `ruta/al/archivo`

_Breve descripción del dataset._

| Variable | Tipo | Descripción | Dominio / valores | Fuente |
|---|---|---|---|---|
| `<variable>` | <tipo> | <qué es> | <valores posibles> | <origen> |

───────────────────────────────────────────────────────────────────────────── -->
