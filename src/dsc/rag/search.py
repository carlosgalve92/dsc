from agent_framework import Agent
from agent_framework.openai import OpenAIEmbeddingClient
from chromadb import Collection

from dsc.constants.common import PROJECT_ROOT
from dsc.utils.common import read_yaml

config_rag = read_yaml(PROJECT_ROOT / "config/rag.yaml")

async def recuperar_fragmentos(
    pregunta: str,
    coleccion: Collection,
    cliente_embeddings: OpenAIEmbeddingClient,
    top_k: int = config_rag["top_k"],
    categoria: str | None = None,
    umbral_distancia: float | None = None,
):
    if coleccion.count() == 0:
        return []

    embedding = await cliente_embeddings.get_embeddings([pregunta])
    parametros = {
        "query_embeddings": [embedding[0].vector],
        "n_results": min(top_k, coleccion.count()),
        "include": ["documents", "metadatas", "distances"],
    }
    if categoria is not None:
        parametros["where"] = {"categoria": categoria}

    resultados = coleccion.query(**parametros)
    fragmentos = [
        {"id": id_chunk, "text": texto, "metadata": metadatos, "distancia": distancia}
        for id_chunk, texto, metadatos, distancia in zip(
            resultados["ids"][0],
            resultados["documents"][0],
            resultados["metadatas"][0],
            resultados["distances"][0],
        )
    ]
    if umbral_distancia is not None:
        fragmentos = [f for f in fragmentos if f["distancia"] <= umbral_distancia]
    return fragmentos


async def preguntar_con_rag(
    pregunta: str,
    agente: Agent,
    coleccion: Collection,
    cliente_embeddings: OpenAIEmbeddingClient,
    categoria: str | None = None,
    s=None,
    ):

    fragmentos = await recuperar_fragmentos(
        pregunta,
        coleccion=coleccion, cliente_embeddings=cliente_embeddings,
        categoria=categoria, umbral_distancia=config_rag["umbral_distancia"]
    )

    if not fragmentos:
        return {
            "respuesta": "No encontré información relacionada en los documentos disponibles.",
            "fragmentos": [],
        }

    contexto = "\n\n".join(
        f"Fuente: {item['metadata']['fuente']} (sección: {item['metadata']['seccion']})\n"
        f"Título: {item['metadata']['titulo']}\n"
        f"Contenido: {item['text']}"
        for item in fragmentos
    )

    consulta = (
        f"CONTEXTO RECUPERADO:\n{contexto}\n\n"
        f"PREGUNTA:\n{pregunta}\n\n"
        "Responde solo si el contexto sustenta la respuesta. "
        "Si no es suficiente, indícalo explícitamente. "
        "Cita la fuente y la sección utilizadas."
    )
    respuesta = await agente.run(consulta, session=s)
    return {"respuesta": respuesta.text, "fragmentos": fragmentos}
