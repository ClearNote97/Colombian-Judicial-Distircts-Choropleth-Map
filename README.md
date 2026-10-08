<div align="center">

# 🗺️ Mapa Judicial de Colombia

**El mapa de la justicia colombiana, reconstruido como un _pipeline de datos reproducible_.**

_Lo valioso de este repo **no es solo el mapa: es el método** — cómo se reconstruyó, desde un PDF
oficial, la geografía judicial de Colombia (que **no coincide** con la división político-administrativa),
de forma rigurosa, trazable y ejecutable con un comando, en colaboración con un agente de IA._

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/deps-uv-DE5FE9)
![GeoPandas](https://img.shields.io/badge/GeoPandas-geoespacial-139C5A)
![matplotlib](https://img.shields.io/badge/matplotlib-viz-11557C)
![Dev Container](https://img.shields.io/badge/Dev-Container-2496ED?logo=docker&logoColor=white)
![Claude Code](https://img.shields.io/badge/hecho%20con-Claude%20Code-D97757?logo=anthropic&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

<br>

<img src="output/mapa_distritos_judiciales.png" alt="División por Distritos Judiciales de Colombia" width="560">

</div>

---

Este fue mi **primer proyecto después de aprender a programar**, hoy reconstruido como un pipeline
profesional. Toma el **PDF oficial del Mapa Judicial** de la Rama Judicial y lo convierte en
**archivos de mapa listos para usar** (GeoJSON, TopoJSON, Excel) de los distritos judiciales de
Colombia, a tres niveles: **municipio → circuito → distrito**. Habilita el análisis geoespacial de mi
línea de investigación, el **análisis económico del derecho (Law & Economics)**.

---

## 🧩 El problema

> **La geografía judicial de Colombia NO coincide con su división político-administrativa.**

Los distritos y circuitos judiciales **cruzan fronteras departamentales**, agrupan municipios de
maneras propias, y no existen como archivo geográfico listo: viven en un **PDF**. Para analizarlos
(coropléticos, tableros, estadística espacial) hay que **reconstruir esa geografía** y cruzarla con
los municipios oficiales — sin perder el rigor de qué municipio pertenece a qué unidad judicial.

---

## 🧠 Cómo se abordó (lo valioso)

El corazón del proyecto es el *método*, no solo el mapa:

1. **El producto, primero.** Se definió que el entregable son **archivos de mapa multinivel**
   importables (no un notebook): municipio, circuito y distrito judicial.
2. **Extracción del PDF.** `camelot` lee la jerarquía Distrito → Circuito → Municipio del PDF oficial
   (una tabla de ~1.100 municipios).
3. **Homologación por código, no por 400 regex.** El reto: el nombre del municipio en el PDF no
   coincide con el oficial del DANE (tildes, abreviaturas, typos). En vez de corregir a mano (como la
   primera versión), se **construye el código DANE** cruzando `nombre normalizado + reglas + el
   "footprint" del distrito`, con una **tabla de override** curada solo para el residuo. Resultado:
   **cobertura 1.104/1.104**, verificable.
4. **Verificación dura, no confianza en el nombre.** Se detectaron y corrigieron casos de *"nombre
   único equivocado"* (p. ej. `SANTUARIO` → El Santuario de Antioquia, no el de Risaralda) por choque
   de códigos, y se separó *"distrito sin dato"* de *"municipio sin juzgado"*.
5. **Geometría oficial.** Se une el código DANE con la geometría municipal del **DANE/MGN** y se hace
   `dissolve` por unidad **judicial** (no por departamento).
6. **Honestidad técnica.** Cuando Plotly no pudo renderizar las geometrías de las áreas no
   municipalizadas de la Amazonía, se diagnosticó con render real y se migró a **matplotlib** — todo
   registrado en la bitácora.
7. **Bitácora de decisiones** (`docs/bitacora-decisiones.md`, `D-001`…`D-007`) como **evidencia del
   razonamiento**: qué se decidió, por qué, qué se descartó y qué cambió.

> **Iteración humano–IA.** El rol humano fue **dirigir**: definir el producto, aportar el insight de los
> códigos, fijar criterios (p. ej. "distrito sin dato = negro") y decidir. El agente **ejecutó**:
> extracción, homologación, verificación, geometría y maquetado, dejando el razonamiento trazado.

---

## 👀 Un vistazo

<div align="center">

| Eficiencia — Juzgados Municipales | Eficiencia — Juzgados de Circuito |
|:---:|:---:|
| <img src="output/choropleth_eficiencia_municipal.png" alt="Eficiencia municipal" width="380"> | <img src="output/choropleth_eficiencia_circuito.png" alt="Eficiencia de circuito" width="380"> |

_Negro = distrito sin dato · Gris = municipio sin juzgado · inset: San Andrés y Providencia._

</div>

---

## ▶️ Cómo correr

> Todo corre **dentro del Dev Container** (ahí viven Python, `uv` y las librerías geoespaciales).

```bash
# 1. Abrir el repo en VS Code → "Reopen in Container" (el postCreate corre `uv sync`)

# 2. Generar el mapa — un solo comando:
uv run python -m judicial_map
#    → deja los archivos en output/
```

**Opciones:**

```bash
uv run python -m judicial_map --niveles distrito            # solo un nivel (municipio|circuito|distrito)
uv run python -m judicial_map --niveles municipio circuito  # varios niveles
uv run python -m judicial_map --no-viz                      # solo los archivos de datos (sin PNG/PDF)
uv run python -m judicial_map --tolerance 0                 # geometría a máximo detalle (archivos pesados)
uv run python -m judicial_map --refresh                     # re-descargar las fuentes (solo si se actualizaron)
```

| Opción | Qué hace |
|---|---|
| `--niveles` | Qué nivel(es) generar (por defecto los tres). |
| `--tolerance` | Suavizado de bordes para aligerar archivos (default `0.001`; `0` = máximo detalle). |
| `--no-viz` | No generar los mapas de ejemplo PNG/PDF. |
| `--refresh` | Ignorar la caché y re-descargar PDF / DIVIPOLA / geometría. |

Tests (el gate): `uv run pytest tests/`.

---

## 📦 Qué produce (en [`output/`](./output/))

Por cada nivel judicial, en tres formatos:

- **`.geojson`** — geometría, para Dash / web / SIG.
- **`.topojson`** — para el **Shape Map de Power BI** (compacto, bordes compartidos). Clave de enlace:
  `cod_dane` (municipio) o `district` (distrito/circuito).
- **`.xlsx`** — atributos sin geometría, para tablas y joins.

Más **mapas de ejemplo** (PNG + PDF, matplotlib) que colorean los distritos por la eficiencia de sus
juzgados usando los datos de ejemplo (`data/other/DB1/DB2 *.xlsx`).

---

## 🔬 Hallazgos

Emergidos del cruce Mapa Judicial × DANE (ver [`docs/hallazgos-geograficos.md`](docs/hallazgos-geograficos.md)):

- **12 municipios** cuyo distrito judicial está en **otro departamento** — y el propio PDF los marca
  con sufijos `(BOY)`, `(CESAR)`, `(CUND)`…
- El distrito de **Villavicencio abarca 6 departamentos** (Meta, Vichada, Guainía, Guaviare, Vaupés + parte de Cundinamarca).
- **20 municipios sin juzgado asignado** (16 son áreas no municipalizadas de la Amazonía) — los vacíos
  del mapa, el hallazgo original del autor.

---

## 🗂️ Estructura

```
.
├── src/judicial_map/    # pipeline: ingest → homologate → merge → export (+ viz) · __main__
├── data/
│   ├── other/           # datos de ejemplo + caché de fuentes
│   └── homologacion/    # tabla de override municipio → código DANE (YAML)
├── output/              # el producto (geojson/topojson/xlsx) + mapas de ejemplo (png/pdf)
├── tests/               # pytest (el gate)
├── docs/
│   ├── bitacora-decisiones.md    # el PORQUÉ de cada decisión (D-001…D-007) — la evidencia del método
│   ├── hallazgos-geograficos.md  # los hallazgos de investigación
│   ├── diccionario-de-datos.md   # qué significa cada variable
│   └── legado/                   # el notebook original, intacto
├── .devcontainer/       # definición del entorno (Dev Container + uv)
├── AGENTS.md            # contrato de trabajo con el agente de IA
└── README.md            # este archivo
```

---

## 🛠️ Stack y herramientas

**Entorno y lenguaje**
- **Python 3.14** con **`uv`** (lockfile reproducible) · **Dev Container + Docker** (VS Code).
- **Plantilla base:** [**ClearNote Py DA**](https://github.com/ClearNote97/ClearNote_Py_DA) — mi plantilla
  de dev container para análisis de datos en Python.

**Datos y geoespacial**
- **camelot** (extracción de tablas del PDF) · **geopandas / shapely / pyproj / pyogrio** ·
  **topojson** · **pandas / numpy** · **openpyxl** · **matplotlib** (mapas estáticos).

**Fuentes**
- **Mapa Judicial** (Rama Judicial) · **DIVIPOLA** (DANE) · **MGN 2024** (DANE, geometría municipal).

**Agente de IA (par de trabajo)**
- Reconstruido en colaboración con **Claude** (Anthropic) vía **Claude Code**, en el marco personal
  de agentes **Helix**. El humano dirige (problema, criterios, insights, decisiones); el agente ejecuta
  y deja el razonamiento trazado.

---

## ⚠️ Nota honesta

Los `.xlsx` de eficiencia (`DB1`/`DB2`) son **datos de ejemplo** para verificar el pipeline, no el
producto. Las fuentes de red (PDF, DANE) pueden cambiar de URL o contenido; por eso se cachean y se
versionan las pequeñas. El valor del repo está en *cómo se reconstruyó y verificó* la geografía judicial.

---

## 🙏 Créditos

- **Plantilla base:** [ClearNote Py DA](https://github.com/ClearNote97/ClearNote_Py_DA) — dev container para análisis de datos en Python.
- **Autor:** MSc. Nicolás Enrique Valencia Santiago.
- **Par de trabajo:** agente de IA (Claude / Claude Code, en el marco [Helix](https://github.com/ftuga/helix_asisten) de [ftuga](https://github.com/ftuga)).
- **Datos:** Rama Judicial de Colombia y DANE (DIVIPOLA, MGN).

## ⚖️ Licencia

[MIT](https://opensource.org/license/MIT).
