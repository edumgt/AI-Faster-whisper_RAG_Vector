from __future__ import annotations
from typing import List
import numpy as np

class EmbedderBase:
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

class SentenceTransformerEmbedder(EmbedderBase):
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True)
        if isinstance(vecs, np.ndarray):
            return vecs.tolist()
        return [v.tolist() for v in vecs]

class OpenAIEmbedder(EmbedderBase):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in resp.data]
