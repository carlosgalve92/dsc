import re

from dsc.constants.common import PROJECT_ROOT
from dsc.utils.common import read_yaml

chunking_config = read_yaml(PROJECT_ROOT / "config/chunking.yaml")

def dividir_por_secciones(contenido: str) -> list[tuple[str, str]]:
    # Divide el texto en (nombre_seccion, texto) usando los encabezados '## '.
    secciones = []
    partes = re.split(r"^## +", contenido, flags=re.MULTILINE)

    # partes[0] = título '# ...' + párrafo introductorio
    intro = re.sub(r"^# .*$", "", partes[0], flags=re.MULTILINE).strip()
    if intro:
        secciones.append(("Introducción", intro))

    for parte in partes[1:]:
        lineas = parte.strip().split("\n", 1)
        nombre = lineas[0].strip()
        texto = lineas[1].strip() if len(lineas) > 1 else ""
        if texto:
            secciones.append((nombre, texto))
    return secciones


def subdividir_con_solapamiento(
    texto: str,
    max_chars: int = chunking_config["max_caracteres"],
    overlap: int = chunking_config["solapamiento"]) -> list[str]:
    # Respaldo para secciones largas: agrupa oraciones completas sin superar max_chars
    # y repite al inicio del siguiente fragmento las últimas oraciones (≈ overlap caracteres).
    if len(texto) <= max_chars:
        return [texto]

    oraciones = re.split(r"(?<=[.!?])\s+", texto)
    fragmentos, actual = [], []
    for oracion in oraciones:
        if actual and len(" ".join(actual + [oracion])) > max_chars:
            fragmentos.append(" ".join(actual))
            # solapamiento: conservar oraciones finales hasta ~overlap caracteres
            arrastre, largo = [], 0
            for o in reversed(actual):
                if largo + len(o) > overlap:
                    break
                arrastre.insert(0, o)
                largo += len(o)
            actual = arrastre
        actual.append(oracion)
    if actual:
        fragmentos.append(" ".join(actual))
    return fragmentos


def generar_chunks(documento: dict) -> list[dict]:
    chunks = []
    numero = 0
    for seccion, texto_seccion in dividir_por_secciones(documento["contenido"]):
        for parte in subdividir_con_solapamiento(texto_seccion):
            numero += 1
            encabezado = f"Documento: {documento['titulo']} | Sección: {seccion}"
            chunks.append({
                "id": f"{documento['id']}_chunk_{numero}",
                "text": f"{encabezado}\n{parte}",
                "metadata": {
                    # --- se muestran como contexto / procedencia ---
                    "fuente": documento["fuente"],
                    "titulo": documento["titulo"],
                    "seccion": seccion,
                    "numero_chunk": numero,
                    # --- se usan como filtros ---
                    "categoria": documento["categoria"],
                    "tipo_documento": documento["tipo_documento"],
                    "documento_id": documento["id"],
                },
            })
    return chunks
