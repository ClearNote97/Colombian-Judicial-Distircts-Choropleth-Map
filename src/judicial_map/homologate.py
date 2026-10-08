"""Homologación: municipio del PDF -> código DANE (para luego pegar geometría).

El código DANE es solo un medio para dar geometría a cada municipio; la agregación
final es por unidad JUDICIAL (distrito/circuito), no por departamento.

Estrategia (reemplaza las ~400 regex del legado):
1. ``normalize`` + ``apply_rules`` (tildes, mayúsculas, PTO->PUERTO, STA->SANTA, sufijo "(DEPTO)").
2. Nombre único en DIVIPOLA -> código directo (resuelve también municipios de nombre
   único en departamentos vecinos, sin importar la frontera departamental).
3. Nombre repetido -> se desambigua por el *footprint* del distrito (los departamentos
   donde caen sus municipios ya resueltos), derivado de los datos, no impuesto.
4. Residuo (typos, renombres oficiales, ambigüedad irresoluble) -> tabla ``override``
   versionada en YAML, keyed por contexto judicial ``distrito :: municipio``.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import yaml

# Sufijos de departamento que el PDF pega entre paréntesis para desambiguar.
_DEPT_SUFFIX = {"CUN", "CUND", "BOY", "NS", "CH", "CESAR", "CAUCA", "ROBLES", "ARMERO"}
_EXPAND = {"PTO": "PUERTO", "STA": "SANTA", "STO": "SANTO"}


def normalize(name: str) -> str:
    """Mayúsculas, sin tildes, sin puntuación, espacios colapsados."""
    s = unicodedata.normalize("NFKD", str(name))
    s = "".join(c for c in s if not unicodedata.combining(c)).upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9]+", " ", s)).strip()


def apply_rules(name: str) -> str:
    """``normalize`` + reglas sistemáticas de abreviatura y sufijo de departamento."""
    toks = normalize(name).split()
    if len(toks) > 1 and toks[-1] in _DEPT_SUFFIX:
        toks = toks[:-1]
    out = []
    for i, t in enumerate(toks):
        if t == "S" and i == 0:
            out.append("SAN")
        else:
            out.append(_EXPAND.get(t, t))
    return " ".join(out)


def load_overrides(path: Path) -> dict[tuple[str, str], str]:
    """Carga el override YAML (``"DISTRITO :: MUNICIPIO": "codigo"``) a dict normalizado."""
    if not path or not Path(path).exists():
        return {}
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    out: dict[tuple[str, str], str] = {}
    for key, code in raw.items():
        if code in (None, "") or "::" not in key:
            continue
        district, municipality = (p.strip() for p in key.split("::", 1))
        out[(normalize(district), normalize(municipality))] = str(code).strip().zfill(5)
    return out


def build_name_index(divipola: pd.DataFrame) -> dict[str, list[dict]]:
    """clave (nombre con reglas) -> lista de candidatos DANE."""
    idx: dict[str, list[dict]] = defaultdict(list)
    for r in divipola.itertuples(index=False):
        idx[apply_rules(r.municipio)].append(
            {"cod_dane": r.cod_dane, "cod_depto": r.cod_depto,
             "departamento": r.departamento, "municipio": r.municipio}
        )
    return idx


@dataclass
class Resolution:
    resolved: pd.DataFrame                     # district, circuit, municipality, cod_dane, match
    unresolved: list[dict] = field(default_factory=list)  # entradas para el override


# Un departamento cuenta como "footprint" de un distrito si tiene al menos este
# número de municipios ya resueltos ahí (filtra ruido de municipios mal matcheados).
MIN_FOOTPRINT = 3


def resolve(
    hierarchy: pd.DataFrame,
    divipola: pd.DataFrame,
    overrides: dict[tuple[str, str], str] | None = None,
) -> Resolution:
    """Asigna ``cod_dane`` a cada municipio del PDF. Devuelve resueltos + pendientes."""
    overrides = overrides or {}
    idx = build_name_index(divipola)
    code2depto = dict(zip(divipola["cod_dane"], divipola["cod_depto"]))

    rows: list[dict] = []
    pending: list[tuple] = []  # (dict_row, key, candidates)

    for r in hierarchy.itertuples(index=False):
        ov_key = (normalize(r.district), normalize(r.municipality))
        base = {"district": r.district, "circuit": r.circuit, "municipality": r.municipality}
        if ov_key in overrides:
            rows.append({**base, "cod_dane": overrides[ov_key], "match": "override"})
            continue
        cands = idx.get(apply_rules(r.municipality), [])
        if len(cands) == 1:
            rows.append({**base, "cod_dane": cands[0]["cod_dane"], "match": "unique"})
        else:
            pending.append((base, apply_rules(r.municipality), cands))

    # footprint del distrito = departamentos donde caen sus municipios ya resueltos
    footprint: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        dep = code2depto.get(row["cod_dane"])
        if dep:
            footprint[row["district"]][dep] += 1

    unresolved: list[dict] = []
    for base, key, cands in pending:
        if len(cands) >= 2:
            fp = {dep for dep, n in footprint.get(base["district"], Counter()).items()
                  if n >= MIN_FOOTPRINT}
            in_fp = [c for c in cands if c["cod_depto"] in fp]
            if len(in_fp) == 1:
                rows.append({**base, "cod_dane": in_fp[0]["cod_dane"], "match": "footprint"})
                continue
            reason = "ambiguo"
        else:
            reason = "sin_match"
        unresolved.append({**base, "key": key, "candidates": cands, "reason": reason})

    resolved = pd.DataFrame(rows, columns=["district", "circuit", "municipality", "cod_dane", "match"])
    return Resolution(resolved=resolved, unresolved=unresolved)
