from dsc.constants.common import PROJECT_ROOT
from dsc.utils.common import read_yaml

chunking_config = read_yaml(PROJECT_ROOT / "config/chunking.yaml")

def evaluar_chunks(chunks: list[dict], documentos: list[dict]) -> None:
    """
    Evalúa los chunks generados según reglas predefinidas y muestra un resumen de la evaluación.
    """
    # Evaluación basada en reglas
    longitudes = [len(c["text"]) for c in chunks]
    ids = [c["id"] for c in chunks]

    checks = {
        "IDs únicos": len(ids) == len(set(ids)),
        "Todos tienen encabezado de documento y sección": all(c["text"].startswith("Documento: ") for c in chunks),
        "Ningún chunk vacío (> 80 caracteres)": min(longitudes) > 80,
        f"Ningún chunk supera {chunking_config['max_caracteres'] + 250} caracteres": max(longitudes) <= chunking_config['max_caracteres'] + 250,
        "Metadatos solo con valores simples": all(
            isinstance(v, (str, int, float, bool)) for c in chunks for v in c["metadata"].values()
        ),
        "Todas las categorías representadas": {c["metadata"]["categoria"] for c in chunks}
            == {d["categoria"] for d in documentos},
    }
    for regla, ok in checks.items():
        print(("✅" if ok else "❌"), regla)
    print(f"\nLongitud mín/prom/máx: {min(longitudes)} / {sum(longitudes)//len(longitudes)} / {max(longitudes)} caracteres")