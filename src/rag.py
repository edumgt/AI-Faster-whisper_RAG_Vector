from __future__ import annotations
from typing import List, Dict, Any
from .schemas import RagHit
from .utils import normalize_text

PERSONA_SYSTEM_SUFFIX: Dict[str, str] = {
    "default": "기본 톤: 객관적이고 균형 잡힌 임상적 요약.",
    "warm": "따뜻한 공감형 톤: 내담자의 정서적 경험을 존중하는 언어를 사용하세요.",
    "coach": "코칭형 톤: 실행 가능한 다음 행동과 실천 질문을 구체적으로 제안하세요.",
    "strict": "구조화·리스크 관리형 톤: 위험 신호, 경계 조건, 관찰 포인트를 명확히 구분하세요.",
}

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


def resolve_persona(persona: str | None) -> str:
    candidate = (persona or "default").strip().lower()
    return candidate if candidate in PERSONA_SYSTEM_SUFFIX else "default"


def build_report_system_prompt(persona: str | None) -> str:
    key = resolve_persona(persona)
    return f"{RAG_REPORT_SYSTEM}\n- 페르소나 지시: {PERSONA_SYSTEM_SUFFIX[key]}"

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
