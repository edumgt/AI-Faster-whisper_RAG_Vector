from __future__ import annotations
from typing import List, Dict, Any
from .schemas import RagHit
from .utils import normalize_text

def format_hits_for_prompt(hits: List[RagHit]) -> str:
    if not hits:
        return "(no relevant history found)"
    lines = []
    for i, h in enumerate(hits, 1):
        lines.append(f"[{i}] session_id={h.session_id} score={h.score:.4f}\n{h.snippet}")
    return "\n\n".join(lines)

RAG_REPORT_SYSTEM = """당신은 상담 기록 기반 리포트 작성 도우미입니다.
- 현재 세션 transcript + 과거 유사 세션 요약(RAG 히스토리)을 함께 보고,
  상담사가 활용할 수 있는 '상황 요약 / 패턴 / 위험 신호 / 개입 아이디어'를 작성하세요.
- 의학적 진단 확정 금지, 텍스트 근거 중심.
- 개인정보(실명/연락처/주소)는 생성하지 마세요.
""".strip()

def build_final_report_prompt(transcript: str, rag_context: str, analysis_json: Dict[str, Any]) -> str:
    return f"""[현재 세션 Transcript]
{normalize_text(transcript)}

[구조화 분석(JSON)]
{analysis_json}

[RAG 히스토리 - 유사 과거 세션]
{rag_context}

요청:
1) 5줄 내외로 현재 세션 핵심 요약
2) 반복 패턴/트리거(있다면)
3) 위험 신호와 보호 요인
4) 다음 세션에서 시도할 질문/개입 아이디어 (불릿 5개)
""".strip()
