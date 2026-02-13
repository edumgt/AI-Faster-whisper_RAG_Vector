from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, Optional, List
import json
import os
from .utils import normalize_text

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
  session_id TEXT PRIMARY KEY,
  client_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  source TEXT NOT NULL,
  transcript TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analyses (
  session_id TEXT PRIMARY KEY,
  analysis_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);
"""

@dataclass
class SessionRow:
    session_id: str
    client_id: str
    created_at: str
    source: str
    transcript: str

class Storage:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA_SQL)

    def upsert_session(self, session_id: str, client_id: str, created_at: str, source: str, transcript: str):
        transcript = normalize_text(transcript)
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO sessions(session_id, client_id, created_at, source, transcript)
                     VALUES(?,?,?,?,?)
                     ON CONFLICT(session_id) DO UPDATE SET
                        client_id=excluded.client_id,
                        created_at=excluded.created_at,
                        source=excluded.source,
                        transcript=excluded.transcript
                """,
                (session_id, client_id, created_at, source, transcript),
            )

    def get_session(self, session_id: str) -> Optional[SessionRow]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
            return SessionRow(**dict(row)) if row else None

    def upsert_analysis(self, session_id: str, created_at: str, analysis: Dict[str, Any]):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO analyses(session_id, analysis_json, created_at)
                     VALUES(?,?,?)
                     ON CONFLICT(session_id) DO UPDATE SET
                        analysis_json=excluded.analysis_json,
                        created_at=excluded.created_at
                """,
                (session_id, json.dumps(analysis, ensure_ascii=False), created_at),
            )

    def get_analysis(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT analysis_json FROM analyses WHERE session_id=?", (session_id,)).fetchone()
            return json.loads(row[0]) if row else None
