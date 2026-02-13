from __future__ import annotations
from typing import Dict, Any, List
from .schemas import AnalysisResult
from .utils import normalize_text

SYSTEM_PROMPT = """당신은 상담 텍스트를 읽고 '심리 상태/갈등 요인/위험도'를 구조화하여 산출하는 분석기입니다.
의학적 진단을 확정하지 말고, 텍스트 근거 기반으로 추정/가설 형태로 작성하세요.
위험도는 자/타해 위험 및 급성 위기 가능성을 0~1로 수치화하되, 근거를 반드시 제시하세요.
""".strip()

SCHEMA_HINT = """{
  "mood": "stable|irritable|anxious|depressed|mixed|unknown",
  "primary_emotions": ["..."],
  "conflict_factors": ["..."],
  "coping_resources": ["..."],
  "risk_score": 0.0,
  "risk_reasons": ["..."],
  "next_questions": ["..."],
  "confidence": 0.0
}
""".strip()

RISK_KEYWORDS_HIGH = ["자해","죽고","죽고싶","극단","끝내고","해치고","칼","약을","투신","자살"]
RISK_KEYWORDS_MED  = ["무가치","절망","더는","못 버티","포기","공황","숨이","불안","우울","무기력"]
ANGER  = ["화","분노","짜증","열받","치밀"]
ANXIETY= ["불안","초조","걱정","긴장","숨이 막","가슴이 답답","공황"]
DEPRESS= ["무기력","우울","의욕","아무것도","지침","피곤"]

def _contains_any(text: str, kws: List[str]) -> bool:
    return any(k in text for k in kws)

def analyze_rule_based(transcript: str) -> AnalysisResult:
    t = normalize_text(transcript)
    risk = 0.10
    reasons: List[str] = []

    if _contains_any(t, RISK_KEYWORDS_HIGH):
        risk = max(risk, 0.85)
        reasons.append("자/타해 관련 표현 또는 급성 위기 키워드 감지")
    elif _contains_any(t, RISK_KEYWORDS_MED):
        risk = max(risk, 0.35)
        reasons.append("우울/불안/절망 관련 표현 감지")

    emotions = []
    mood = "unknown"
    if _contains_any(t, ANGER):
        emotions.append("분노")
        mood = "irritable"
    if _contains_any(t, ANXIETY):
        emotions.append("불안")
        mood = "anxious" if mood == "unknown" else "mixed"
    if _contains_any(t, DEPRESS):
        emotions.append("무기력/우울")
        mood = "depressed" if mood == "unknown" else "mixed"

    conflict = []
    if any(k in t for k in ["팀","상사","팀장","회사","프로젝트","일정","회의"]):
        conflict.append("직장/업무 갈등")
    if any(k in t for k in ["가족","부모","집"]):
        conflict.append("가족 갈등")
    if any(k in t for k in ["연인","남친","여친"]):
        conflict.append("연인/관계 갈등")

    next_q = [
        "최근 수면/식사 패턴은 어떤가요?",
        "가장 힘들었던 순간을 0~10으로 평가하면 몇 점인가요?",
        "지지해주는 사람(동료/가족/친구)이 있나요?",
        "자해/자살 생각이 스쳐간 적이 있는지(있다면 빈도/계획/수단) 확인이 필요합니다.",
    ]

    return AnalysisResult(
        mood=mood,
        primary_emotions=emotions,
        conflict_factors=conflict,
        coping_resources=[],
        risk_score=float(round(risk, 2)),
        risk_reasons=reasons or ["명시적 위기 신호는 낮으나 스트레스/정서 불편 신호 존재"],
        next_questions=next_q,
        confidence=0.45,
    )

def analyze_with_llm(llm, transcript: str) -> AnalysisResult:
    t = normalize_text(transcript)
    data: Dict[str, Any] = llm.chat_json(SYSTEM_PROMPT, f"상담 텍스트:\n{t}", SCHEMA_HINT)
    return AnalysisResult.model_validate(data)

def analyze(transcript: str, llm=None) -> AnalysisResult:
    if llm is None:
        return analyze_rule_based(transcript)
    try:
        return analyze_with_llm(llm, transcript)
    except Exception:
        return analyze_rule_based(transcript)
