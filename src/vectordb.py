from __future__ import annotations
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

class VectorStore:
    def __init__(self, persist_dir: str, collection: str = "counseling_sessions"):
        self.client = chromadb.PersistentClient(path=persist_dir, settings=ChromaSettings(anonymized_telemetry=False))
        self.col = self.client.get_or_create_collection(name=collection)

    def upsert(self, ids: List[str], embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]):
        self.col.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    def query(self, query_embedding: List[float], top_k: int = 4, where: Optional[Dict[str, Any]] = None):
        return self.col.query(query_embeddings=[query_embedding], n_results=top_k, where=where)
