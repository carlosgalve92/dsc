import asyncio

import pandas as pd
from agent_framework import Agent

from dsc.constants.evaluation import TEST_MSJ_ALCANCE_AGENT


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


if __name__ == "__main__":
    print(TEST_MSJ_ALCANCE_AGENT)
