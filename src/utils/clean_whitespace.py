"""Limpieza de espacios en blanco en DataFrames.

Primer paso del flujo de procesamiento: normaliza los nombres de columna y las
celdas de texto, convierte cadenas vacías en NaN y elimina filas totalmente vacías.
"""

import re

import numpy as np
import pandas as pd


def limpiar_espacios_en_blanco(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza espacios en los nombres de columna y en las celdas de texto.

    - Recorta los extremos y colapsa espacios internos en los nombres de columna de tipo texto.
    - Hace lo mismo en las celdas de texto.
    - Convierte cadenas vacías en NaN y elimina las filas completamente vacías.

    No modifica el DataFrame original.
    """
    df = df.copy()

    # Nombres de columna de tipo texto: colapsar espacios internos y recortar extremos
    df.columns = [
        re.sub(r"\s+", " ", col).strip() if isinstance(col, str) else col
        for col in df.columns
    ]

    # Celdas de texto: recortar extremos y colapsar espacios internos
    df = df.replace(r"^\s+|\s+$", "", regex=True)
    df = df.replace(r"\s+", " ", regex=True)

    # Cadenas vacías -> NaN; luego descartar filas totalmente vacías
    df = df.replace("", np.nan)
    df = df.dropna(how="all")

    return df
