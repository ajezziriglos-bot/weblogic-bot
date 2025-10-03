# src/vectorstore.py
from typing import List, Dict, Any
import chromadb
from .config import settings

# Cliente persistente (0.5.x) — persiste automáticamente en disco
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DIR)

COLLECTION_NAME = "kb_main"  # 3–63 chars, alfanum/underscore/hyphen

# Crear u obtener la colección
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

def add_docs(
    ids: List[str],
    documents: List[str],
    metadatas: List[Dict[str, Any]],
    embeddings: List[List[float]],
):
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    # En 0.5.x NO hay persist(); se guarda automáticamente

def clear_collection():
    global collection
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

def get_collection():
    return collection

def query(q_emb: List[float], top_k: int):
    return collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )