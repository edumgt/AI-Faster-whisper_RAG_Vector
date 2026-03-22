#!/usr/bin/env python3
"""
ChromaDB 정신분석학 지식 베이스 구축 스크립트
Builds the Chroma vector DB from the psychoanalysis seed data.

Usage:
    python scripts/build_psycho_chroma.py [--chroma-dir runtime/chroma_store]
                                          [--seed samples/psychoanalysis_seed.jsonl]
                                          [--collection psychoanalysis_knowledge]
                                          [--model sentence-transformers/all-MiniLM-L6-v2]
                                          [--batch-size 32]

This script:
1. Reads the psychoanalysis JSONL seed file
2. Generates embeddings using sentence-transformers
3. Upserts into the specified Chroma collection
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List


def load_records(seed_path: Path) -> List[Dict]:
    records = []
    for line in seed_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"[warn] Skipping malformed line: {exc}", file=sys.stderr)
    return records


def make_doc_id(record: Dict, index: int) -> str:
    """Create a stable, deterministic document ID."""
    key = f"{record.get('source','')}-{record.get('category','')}-{record.get('topic','')}-{index}"
    return "psych_" + hashlib.md5(key.encode("utf-8")).hexdigest()[:16]


def batch(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def build(
    seed_path: Path,
    chroma_dir: str,
    collection_name: str,
    model_name: str,
    batch_size: int,
):
    # ---- Load records ----
    if not seed_path.exists():
        print(f"[error] Seed file not found: {seed_path}", file=sys.stderr)
        sys.exit(1)

    records = load_records(seed_path)
    print(f"Loaded {len(records)} records from {seed_path}", file=sys.stderr)

    # ---- Init Chroma ----
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    Path(chroma_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=chroma_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    col = client.get_or_create_collection(name=collection_name)
    print(f"Chroma collection '{collection_name}' ready at {chroma_dir}", file=sys.stderr)

    # ---- Init embedder ----
    from sentence_transformers import SentenceTransformer
    import numpy as np

    print(f"Loading embedding model '{model_name}' ...", file=sys.stderr)
    model = SentenceTransformer(model_name)

    # ---- Embed & upsert in batches ----
    total_upserted = 0
    global_index = 0
    for chunk in batch(records, batch_size):
        texts = [r.get("text", "") for r in chunk]
        ids = [make_doc_id(r, global_index + i) for i, r in enumerate(chunk)]
        metadatas = [
            {
                "source": r.get("source", "psychoanalysis"),
                "category": r.get("category", ""),
                "topic": r.get("topic", ""),
            }
            for r in chunk
        ]

        vecs = model.encode(texts, normalize_embeddings=True)
        if isinstance(vecs, np.ndarray):
            embeddings = vecs.tolist()
        else:
            embeddings = [v.tolist() for v in vecs]

        col.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        global_index += len(chunk)
        total_upserted += len(chunk)
        print(f"  Upserted {total_upserted}/{len(records)} ...", file=sys.stderr)

    print(
        f"\nDone. {total_upserted} documents in collection '{collection_name}'.",
        file=sys.stderr,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Build Chroma vector DB from psychoanalysis seed data"
    )
    parser.add_argument(
        "--chroma-dir",
        default="runtime/chroma_store",
        help="Path to ChromaDB persist directory (default: runtime/chroma_store)",
    )
    parser.add_argument(
        "--seed",
        default="samples/psychoanalysis_seed.jsonl",
        help="Input JSONL seed file (default: samples/psychoanalysis_seed.jsonl)",
    )
    parser.add_argument(
        "--collection",
        default="psychoanalysis_knowledge",
        help="Chroma collection name (default: psychoanalysis_knowledge)",
    )
    parser.add_argument(
        "--model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence-transformers model name",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Embedding batch size (default: 32)",
    )
    args = parser.parse_args()

    build(
        seed_path=Path(args.seed),
        chroma_dir=args.chroma_dir,
        collection_name=args.collection,
        model_name=args.model,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
