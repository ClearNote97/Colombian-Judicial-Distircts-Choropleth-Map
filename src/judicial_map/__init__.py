"""judicial_map — pipeline del Mapa Judicial de Colombia.

Construye los archivos de mapa (geojson/json/xlsx) de los distritos judiciales
de Colombia a distintos niveles (municipio, circuito, distrito, departamento),
listos para importar en Power BI, Dash u otras herramientas.

Flujo: ingest -> homologate -> merge -> export (+ viz opcional).
"""

__version__ = "1.0.0"
