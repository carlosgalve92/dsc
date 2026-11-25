import chromadb

from dsc.constants.common import PROJECT_ROOT
from dsc.utils.common import read_yaml

config_rag = read_yaml(PROJECT_ROOT / "config/rag.yaml")

chroma = chromadb.PersistentClient(path=PROJECT_ROOT / config_rag["path_db"])
coleccion_chroma = chroma.get_or_create_collection(
    name=config_rag["nombre_coleccion"],
    embedding_function=None,
    configuration={"hnsw": {"space": "cosine"}},
)

print("coleccion_chroma:", coleccion_chroma)
