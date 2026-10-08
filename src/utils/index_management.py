"""Consolidación de identificadores únicos entre varios DataFrames."""

from typing import Literal

import pandas as pd


def consolidar_ids_unicos(
    dataframes: list[pd.DataFrame],
    col_id: str = "ID",
    return_as: Literal["dataframe", "list", "set"] = "dataframe",
    set_index: bool = True,
) -> pd.DataFrame | list | set:
    """Consolida los IDs únicos presentes en varios DataFrames.

    Parameters
    ----------
    dataframes : list of pd.DataFrame
        DataFrames a consolidar.
    col_id : str, default 'ID'
        Nombre de la columna con el identificador único.
    return_as : {'dataframe', 'list', 'set'}, default 'dataframe'
        - 'dataframe': DataFrame con la columna de IDs.
        - 'list': lista ordenada de IDs únicos.
        - 'set': conjunto de IDs únicos.
    set_index : bool, default True
        Si es True y `return_as='dataframe'`, usa `col_id` como índice.

    Returns
    -------
    pd.DataFrame, list or set
        Según `return_as`.

    Raises
    ------
    ValueError
        Si `dataframes` está vacío o `return_as` no es válido.
    KeyError
        Si algún DataFrame no tiene la columna `col_id`.
    """
    if not dataframes:
        raise ValueError("La lista de DataFrames está vacía")

    unique_ids: set = set()
    for df in dataframes:
        if col_id not in df.columns:
            raise KeyError(f"La columna '{col_id}' no existe en uno de los DataFrames")
        unique_ids |= set(df[col_id].dropna().unique())

    print(f"✅ Total de IDs únicos consolidados: {len(unique_ids)}")

    if return_as == "set":
        return unique_ids
    if return_as == "list":
        return sorted(unique_ids)
    if return_as == "dataframe":
        df_result = pd.DataFrame(sorted(unique_ids), columns=[col_id])
        if set_index:
            df_result = df_result.set_index(col_id)
        return df_result

    raise ValueError("return_as debe ser 'dataframe', 'list' o 'set'")
