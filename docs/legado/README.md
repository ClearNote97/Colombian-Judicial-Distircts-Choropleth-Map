# `docs/legado/` — versión original del proyecto

Aquí vive, **intacta**, la primera versión del proyecto: el notebook monolítico con el que nació
el mapa coroplético de los distritos judiciales de Colombia. Se conserva como **legado** por su
valor histórico y de referencia — fue el primer proyecto de programación del autor.

| Archivo | Qué es |
|---|---|
| `Colombian Judicial District's Map.ipynb` | Notebook original (~15 MB, con el output renderizado embebido). Pipeline completo en un solo archivo: extracción del PDF con `camelot`, homologación de nombres por regex, merges con DIVIPOLA y shapefile, `dissolve` por nivel y los dos choropleths de Plotly. |
| `README-original.md` | El README narrativo original (voz educativa en plural "we"). |

> **No se modifica.** La re-implementación profesional (pipeline de scripts) vive en `src/` y su
> salida en `output/`. Este directorio es solo memoria del punto de partida.
