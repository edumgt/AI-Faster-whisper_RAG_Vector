from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "none").lower()  # none|openai|ollama
    embed_provider: str = os.getenv("EMBED_PROVIDER", "sentence-transformers").lower()

    # OpenAI
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL") or None
    openai_embed_model: str = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

    # Ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    # sentence-transformers
    st_model: str = os.getenv("ST_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # RAG
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "4"))

    # runtime
    runtime_dir: str = os.getenv("RUNTIME_DIR", "runtime")
    db_path: str = os.getenv("DB_PATH", os.path.join(runtime_dir, "app.db"))
    chroma_dir: str = os.getenv("CHROMA_DIR", os.path.join(runtime_dir, "chroma_store"))
