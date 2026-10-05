"""Tests de homologación: normalización, reglas y resolución a código DANE."""
import pandas as pd

from judicial_map import homologate


# --- funciones puras (sin datos) ---
def test_normalize_strips_accents_and_case():
    assert homologate.normalize("Jericó") == "JERICO"
    assert homologate.normalize("  Bogotá, D.C. ") == "BOGOTA D C"


def test_apply_rules_expansions():
    assert homologate.apply_rules("PTO BERRIO") == "PUERTO BERRIO"
    assert homologate.apply_rules("STA BARBARA") == "SANTA BARBARA"
    assert homologate.apply_rules("S ANTONIO DEL TEQUENDAMA") == "SAN ANTONIO DEL TEQUENDAMA"


def test_apply_rules_strips_department_suffix():
    assert homologate.apply_rules("CUBARÁ (BOY)") == "CUBARA"
    assert homologate.apply_rules("MEDINA (CUN)") == "MEDINA"


# --- caso vacío ---
def test_resolve_empty_hierarchy(divipola):
    empty = pd.DataFrame(columns=["district", "circuit", "municipality"])
    res = homologate.resolve(empty, divipola)
    assert len(res.resolved) == 0
    assert res.unresolved == []


# --- integración (usa caché) ---
def test_full_coverage(resolution, hierarchy):
    assert len(resolution.resolved) == len(hierarchy)
    assert len(resolution.unresolved) == 0


def test_codes_are_five_digits(resolution):
    assert (resolution.resolved["cod_dane"].str.len() == 5).all()


def _code(resolution, district, municipality):
    r = resolution.resolved
    m = r[(r["district"] == district) & (r["municipality"] == municipality)]
    return m["cod_dane"].iloc[0]


def test_curated_overrides(resolution):
    # capitales con nombre oficial largo
    assert _code(resolution, "CALI", "CALI") == "76001"            # Santiago de Cali
    assert _code(resolution, "CARTAGENA", "CARTAGENA") == "13001"  # Cartagena de Indias
    # decisión de dominio: corregimiento
    assert _code(resolution, "VILLAVICENCIO", "SANTA RITA") == "99773"  # Cumaribo
    # "nombre único equivocado" corregido
    assert _code(resolution, "ANTIOQUIA", "SANTUARIO") == "05697"  # El Santuario (no Risaralda)
