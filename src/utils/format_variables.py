"""Conversión de formatos de variables (fechas, enteros, decimales).

Cada función recorre las columnas indicadas, convierte las que existen y reporta por
consola las que fallan, sin interrumpir el resto del DataFrame.
"""

from typing import Literal

import pandas as pd

TimestampUnit = Literal["ms", "s", "excel"]


def _parse_a_datetime(
    serie: pd.Series,
    date_format: str | None,
    timestamp_unit: TimestampUnit | None,
) -> pd.Series:
    """Parsea una serie a datetime, distinguiendo numérico de texto. Lanza en error."""
    if pd.api.types.is_numeric_dtype(serie):
        if timestamp_unit == "ms":
            return pd.to_datetime(serie, unit="ms", errors="raise")
        if timestamp_unit == "s":
            return pd.to_datetime(serie, unit="s", errors="raise")
        if timestamp_unit == "excel":
            return pd.to_datetime("1899-12-30") + pd.to_timedelta(serie, unit="D")
        # Inferir: valores muy grandes suelen venir en milisegundos
        unidad = "ms" if serie.max() > 1e12 else "s"
        return pd.to_datetime(serie, unit=unidad, errors="raise")
    return pd.to_datetime(serie, format=date_format, errors="raise")


def _formatear_temporal(
    df: pd.DataFrame,
    columns: list[str],
    date_format: str | None,
    timestamp_unit: TimestampUnit | None,
    conservar_hora: bool,
) -> pd.DataFrame:
    """Núcleo compartido por `format_dates` y `format_datetime`."""
    for col in columns:
        if col not in df.columns:
            continue
        try:
            convertida = _parse_a_datetime(df[col], date_format, timestamp_unit)
            df[col] = convertida if conservar_hora else convertida.dt.normalize()
        except (ValueError, TypeError) as e:
            print(f"Error formateando columna {col}: {e}")
            invalidos = df.loc[pd.to_datetime(df[col], errors="coerce").isna(), col]
            print(f"Valores problemáticos en columna {col}: {invalidos.unique()}")
    return df


def format_dates(
    df: pd.DataFrame,
    columns: list[str],
    date_format: str | None = None,
    timestamp_unit: TimestampUnit | None = None,
) -> pd.DataFrame:
    """Convierte columnas a fecha, **descartando la hora** (queda a medianoche).

    - `columns`: columnas a convertir (las que no existan se ignoran).
    - `date_format`: formato para columnas de texto (opcional; si falta, se infiere).
    - `timestamp_unit`: para columnas numéricas — `"ms"`, `"s"` o `"excel"`; si falta, se infiere.

    Para conservar la hora, usa `format_datetime`.
    """
    return _formatear_temporal(df, columns, date_format, timestamp_unit, conservar_hora=False)


def format_datetime(
    df: pd.DataFrame,
    columns: list[str],
    date_format: str | None = None,
    timestamp_unit: TimestampUnit | None = None,
) -> pd.DataFrame:
    """Convierte columnas a fecha y hora, **conservando la hora**.

    Misma firma que `format_dates`; la única diferencia es que no descarta el componente horario.
    """
    return _formatear_temporal(df, columns, date_format, timestamp_unit, conservar_hora=True)


def format_int(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convierte columnas a entero **nullable** (`Int64`), tolerando NaN."""
    for col in columns:
        if col in df.columns:
            try:
                df[col] = df[col].astype("Int64")
            except (ValueError, TypeError) as e:
                print(f"Error formateando columna {col}: {e}")
    return df


def format_flt(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convierte columnas a decimal (`float64`)."""
    for col in columns:
        if col in df.columns:
            try:
                df[col] = df[col].astype("float64")
            except (ValueError, TypeError) as e:
                print(f"Error formateando columna {col}: {e}")
    return df
