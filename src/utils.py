from __future__ import annotations
import re
from typing import List

def normalize_text(s: str) -> str:
    s = s.replace("\u200b", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def safe_filename(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("_")
    return name or "file"
