from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class IngestTextIn(BaseModel):
    client_id: str = Field(..., min_length=1)
    transcript: str = Field(..., min_length=1)

class AnalysisResult(BaseModel):
    mood: Literal["stable","irritable","anxious","depressed","mixed","unknown"] = "unknown"
    primary_emotions: List[str] = Field(default_factory=list)
    conflict_factors: List[str] = Field(default_factory=list)
    coping_resources: List[str] = Field(default_factory=list)
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_reasons: List[str] = Field(default_factory=list)
    next_questions: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

class RagHit(BaseModel):
    session_id: str
    client_id: str
    score: float
    snippet: str

class ReportOut(BaseModel):
    session_id: str
    client_id: str
    transcript: str
    analysis: AnalysisResult
    rag_hits: List[RagHit] = Field(default_factory=list)
    final_report: Optional[str] = None
