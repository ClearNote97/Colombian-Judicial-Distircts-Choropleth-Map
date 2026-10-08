"""Fixtures compartidos. Agrega src/ al path y carga datos desde caché (skip si falta)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from judicial_map import config, homologate, ingest  # noqa: E402


def _require(path: Path) -> None:
    if not Path(path).exists():
        pytest.skip(f"falta caché: {path} (corre el pipeline una vez)")


@pytest.fixture(scope="session")
def hierarchy():
    _require(config.CACHE / config.PDF_CACHE_NAME)
    return ingest.load_judicial_hierarchy()


@pytest.fixture(scope="session")
def divipola():
    _require(config.CACHE / config.DIVIPOLA_CACHE_NAME)
    return ingest.load_divipola()


@pytest.fixture(scope="session")
def overrides():
    return homologate.load_overrides(config.OVERRIDE_MUNICIPIOS_YAML)


@pytest.fixture(scope="session")
def resolution(hierarchy, divipola, overrides):
    return homologate.resolve(hierarchy, divipola, overrides=overrides)


@pytest.fixture(scope="session")
def geometries(divipola):
    _require(config.CACHE / config.MGN_CACHE_NAME)
    return ingest.load_municipal_geometries(sorted(divipola["cod_depto"].unique()))
