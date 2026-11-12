from pathlib import Path
from typing import Any

import yaml


def read_yaml(ruta: str | Path) -> dict[str, Any]:
    """Lee un archivo YAML y devuelve su contenido como diccionario."""
    with Path(ruta).open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}