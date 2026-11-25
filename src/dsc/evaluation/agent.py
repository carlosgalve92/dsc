import asyncio
import re

import pandas as pd
from agent_framework import Agent

from dsc.constants.evaluation import FRASES_NEGACION, TEST_MSJ_ALCANCE_AGENT
from dsc.preprocess.text import normalizar


async def valid_agent(
    agente: Agent,
    dc_pruebas: dict = TEST_MSJ_ALCANCE_AGENT,
    max_intentos: int = 3,
    verbose: bool = True,
) -> pd.DataFrame:
    """Ejecuta cada mensaje de prueba de forma independiente y guarda las respuestas."""
    ls_resultados = []
    for categoria, ls_mensajes in dc_pruebas.items():
        for mensaje in ls_mensajes:
            for intento in range(max_intentos):
                try:
                    resultado = await agente.run(mensaje)
                    respuesta = resultado.text
                    break
                except Exception as e:
                    if intento == (max_intentos - 1):
                        respuesta = f"ERROR: {e}"
                    await asyncio.sleep(30 * (intento + 1))

            ls_resultados.append({
                "categoria": categoria,
                "mensaje": mensaje,
                "respuesta": respuesta,
            })
            if verbose:
                print(f"[{categoria}] {mensaje}\n→ {respuesta}\n{'-' * 80}")

    df = pd.DataFrame(ls_resultados)
    return df


def pre_evaluar_con_rag(prueba, salida, frases_negacion: list[str] = FRASES_NEGACION) -> tuple[str, str]:
    respuesta = normalizar(salida["respuesta"])
    secciones = [f["metadata"]["seccion"] for f in salida["fragmentos"]]
    recupero_ok = prueba["chunk_esperado"] is None or any(prueba["chunk_esperado"] in s for s in secciones)

    if prueba["debe_negar"]:
        nego = any(normalizar(f) in respuesta for f in frases_negacion)
        inventa_cifra = bool(re.search(r"\d+([.,]\d+)?\s*%\s*(e\.?a|efectivo)", respuesta))
        if nego and not inventa_cifra:
            return "correcto", "Reconoce que no hay evidencia suficiente y no inventa cifras."
        if nego:
            return "parcial", "Reconoce falta de información, pero menciona alguna cifra: revisar."
        return "incorrecto", "No declara falta de información: posible alucinación."

    faltantes = [k for k in prueba["debe_contener"] if normalizar(k) not in respuesta]
    if recupero_ok and not faltantes:
        return "correcto", "Recupera el chunk esperado y la respuesta contiene la evidencia."
    if recupero_ok or len(faltantes) < len(prueba["debe_contener"]):
        return "parcial", f"Recuperación ok={recupero_ok}; falta en la respuesta: {faltantes}"
    return "incorrecto", f"No recupera el chunk esperado y falta: {faltantes}"
