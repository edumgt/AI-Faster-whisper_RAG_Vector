#!/usr/bin/env python3
"""
정신분석학 콘텐츠 크롤러
Crawls and collects psychoanalysis knowledge content for the Chroma vector DB.

Usage:
    python scripts/crawl_psychoanalysis.py [--output samples/psychoanalysis_seed.jsonl]

The script:
1. Loads the built-in psychoanalysis corpus (Korean)
2. Optionally fetches additional content from Wikipedia (Korean) if network available
3. Deduplicates and saves to the output JSONL file
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Wikipedia Korean API helper
# ---------------------------------------------------------------------------

WIKI_PAGES = [
    "정신분석학",
    "지그문트_프로이트",
    "카를_구스타프_융",
    "방어기제",
    "전이_(심리학)",
    "애착이론",
    "대상관계이론",
    "자아_심리학",
    "자기심리학",
    "오이디푸스_콤플렉스",
    "무의식",
    "억압_(심리학)",
    "투사_(심리학)",
    "승화_(심리학)",
    "경계선_성격장애",
    "자기애성_인격장애",
    "외상후_스트레스_장애",
    "우울장애",
    "불안장애",
    "해리_(심리학)",
]

WIKI_API = "https://ko.wikipedia.org/api/rest_v1/page/summary/{title}"


def _fetch_wiki(title: str, timeout: int = 10) -> Optional[Dict]:
    """Fetch a Wikipedia page summary via REST API."""
    try:
        import urllib.request
        url = WIKI_API.format(title=title)
        req = urllib.request.Request(url, headers={"User-Agent": "psycho-chroma-crawler/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            extract = data.get("extract", "").strip()
            page_title = data.get("title", title)
            if extract and len(extract) > 100:
                return {"title": page_title, "extract": extract}
    except Exception as exc:
        print(f"  [warn] Could not fetch '{title}': {exc}", file=sys.stderr)
    return None


def crawl_wikipedia(pages: List[str], delay: float = 1.0) -> List[Dict]:
    """Crawl Wikipedia Korean pages and return structured records."""
    records = []
    for title in pages:
        print(f"  Fetching Wikipedia: {title} ...", file=sys.stderr)
        result = _fetch_wiki(title)
        if result:
            # Split long extracts into paragraphs; skip very short ones
            paragraphs = [p.strip() for p in result["extract"].split("\n") if p.strip()]
            for para in paragraphs:
                if len(para) < 60:
                    continue
                # Chunk long paragraphs into ≤ 500-char pieces
                for start in range(0, len(para), 500):
                    chunk = para[start : start + 500].strip()
                    if chunk:
                        records.append({
                            "source": "wikipedia_ko",
                            "category": "wikipedia",
                            "topic": result["title"],
                            "text": chunk,
                        })
        time.sleep(delay)
    return records


# ---------------------------------------------------------------------------
# Load built-in corpus
# ---------------------------------------------------------------------------

def load_builtin(seed_path: Path) -> List[Dict]:
    records = []
    if seed_path.exists():
        for line in seed_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def dedup(records: List[Dict]) -> List[Dict]:
    seen: set = set()
    out = []
    for r in records:
        h = hashlib.md5(r.get("text", "").encode("utf-8")).hexdigest()
        if h not in seen:
            seen.add(h)
            out.append(r)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Psychoanalysis content crawler for Chroma DB")
    parser.add_argument(
        "--input",
        default="samples/psychoanalysis_seed.jsonl",
        help="Existing seed JSONL to load as base corpus (default: samples/psychoanalysis_seed.jsonl)",
    )
    parser.add_argument(
        "--output",
        default="samples/psychoanalysis_seed.jsonl",
        help="Output JSONL file path (default: samples/psychoanalysis_seed.jsonl)",
    )
    parser.add_argument(
        "--no-wikipedia",
        action="store_true",
        default=False,
        help="Skip Wikipedia crawling (use built-in corpus only)",
    )
    parser.add_argument(
        "--wiki-delay",
        type=float,
        default=1.0,
        help="Seconds to wait between Wikipedia requests (default: 1.0)",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Load built-in corpus from the input seed file
    input_path = Path(args.input)
    print(f"Loading built-in psychoanalysis corpus from {input_path} ...", file=sys.stderr)
    records = load_builtin(input_path)
    print(f"  Built-in records: {len(records)}", file=sys.stderr)

    # Step 2: Wikipedia crawl (optional)
    if not args.no_wikipedia:
        print("Crawling Wikipedia (Korean) ...", file=sys.stderr)
        wiki_records = crawl_wikipedia(WIKI_PAGES, delay=args.wiki_delay)
        print(f"  Wikipedia records collected: {len(wiki_records)}", file=sys.stderr)
        records.extend(wiki_records)

    # Step 3: Deduplicate
    before = len(records)
    records = dedup(records)
    print(f"Deduplication: {before} → {len(records)} records", file=sys.stderr)

    # Step 4: Save
    with output_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Saved {len(records)} records → {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
