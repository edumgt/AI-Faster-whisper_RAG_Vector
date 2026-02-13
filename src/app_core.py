from __future__ import annotations
from typing import Optional, List
import os, uuid, datetime, json

from .config import Settings
from .storage import Storage
from .vectordb import VectorStore
from .embeddings import SentenceTransformerEmbedder, OpenAIEmbedder
from .analysis import analyze
from .rag import format_hits_for_prompt, RAG_REPORT_SYSTEM, build_final_report_prompt
from .schemas import RagHit, AnalysisResult

def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")

def init_runtime_dirs(settings: Settings):
    os.makedirs(settings.runtime_dir, exist_ok=True)
    os.makedirs(settings.chroma_dir, exist_ok=True)

def make_llm(settings: Settings):
    if settings.llm_provider == "none":
        return None
    if settings.llm_provider == "ollama":
        from .llm import OllamaLLM
        return OllamaLLM(settings.ollama_base_url, settings.ollama_model)
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for LLM_PROVIDER=openai")
        from .llm import OpenAILLM
        return OpenAILLM(settings.openai_api_key, settings.openai_model, settings.openai_base_url)
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")

def make_embedder(settings: Settings):
    if settings.embed_provider == "sentence-transformers":
        return SentenceTransformerEmbedder(settings.st_model)
    if settings.embed_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for EMBED_PROVIDER=openai")
        return OpenAIEmbedder(settings.openai_api_key, settings.openai_embed_model, settings.openai_base_url)
    raise ValueError(f"Unknown EMBED_PROVIDER: {settings.embed_provider}")

def ingest_transcript(settings: Settings, client_id: str, transcript: str, source: str) -> str:
    init_runtime_dirs(settings)
    store = Storage(settings.db_path)
    vdb = VectorStore(settings.chroma_dir)
    embedder = make_embedder(settings)

    session_id = uuid.uuid4().hex[:12]
    created_at = _now_iso()
    store.upsert_session(session_id, client_id, created_at, source, transcript)

    llm = make_llm(settings)
    analysis_res = analyze(transcript, llm=llm)
    store.upsert_analysis(session_id, created_at, analysis_res.model_dump())

    emb = embedder.embed([transcript])[0]
    vdb.upsert(
        ids=[session_id],
        embeddings=[emb],
        documents=[transcript],
        metadatas=[{"client_id": client_id, "created_at": created_at, "source": source}],
    )
    return session_id

def rag_search(settings: Settings, client_id: str, transcript: str) -> List[RagHit]:
    vdb = VectorStore(settings.chroma_dir)
    embedder = make_embedder(settings)

    qemb = embedder.embed([transcript])[0]
    res = vdb.query(qemb, top_k=settings.rag_top_k, where={"client_id": client_id})

    hits: List[RagHit] = []
    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    dists = res.get("distances", [[]])[0]
    for sid, doc, dist in zip(ids, docs, dists):
        if not sid:
            continue
        score = float(1.0 / (1.0 + float(dist)))
        snippet = (doc[:260] + "...") if len(doc) > 260 else doc
        hits.append(RagHit(session_id=sid, client_id=client_id, score=score, snippet=snippet))
    return hits

def build_report(settings: Settings, client_id: str, session_id: str):
    store = Storage(settings.db_path)
    sess = store.get_session(session_id)
    if not sess:
        raise RuntimeError(f"Session not found: {session_id}")
    if sess.client_id != client_id:
        raise RuntimeError("client_id mismatch")

    analysis_json = store.get_analysis(session_id) or {}
    analysis = AnalysisResult.model_validate(analysis_json)

    hits = rag_search(settings, client_id, sess.transcript)
    rag_context = format_hits_for_prompt(hits)

    final_report: Optional[str] = None
    llm = make_llm(settings)
    if llm is not None:
        prompt = build_final_report_prompt(sess.transcript, rag_context, analysis_json)
        try:
            final_report = llm.chat_text(RAG_REPORT_SYSTEM, prompt)
        except Exception:
            final_report = None

    return {
        "session_id": session_id,
        "client_id": client_id,
        "transcript": sess.transcript,
        "analysis": analysis.model_dump(),
        "rag_hits": [h.model_dump() for h in hits],
        "final_report": final_report,
    }
