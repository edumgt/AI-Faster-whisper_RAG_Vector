# Chapter 01. 프로젝트 개요와 전체 아키텍처

## 1) 이 프로젝트가 해결하는 문제
이 저장소는 **상담 텍스트/오디오를 입력받아 분석하고**, 과거 유사 사례를 찾아(RAG), 최종 상담 리포트(JSON/PDF)를 생성하는 데모 시스템입니다.

핵심 목표는 다음 4가지입니다.
- 상담 세션 데이터 수집(텍스트/오디오)
- 위험도/감정/갈등요인 구조화 분석
- 과거 유사 세션 검색(RAG)
- 사람이 읽기 쉬운 최종 리포트 생성

---

## 2) 구성요소 한눈에 보기
시스템은 크게 6개 계층으로 나뉩니다.

1. **Frontend**: Tailwind 기반 단일 페이지(`api/frontend/index.html`)
2. **API 계층**: FastAPI 라우터(`api/main.py`, `api/routes.py`)
3. **도메인 코어**: 파이프라인 오케스트레이션(`src/app_core.py`)
4. **AI 처리**: 분석/임베딩/LLM/STT(`src/analysis.py`, `src/embeddings.py`, `src/llm.py`, `src/stt.py`)
5. **저장 계층**: SQLite + ChromaDB(`src/storage.py`, `src/vectordb.py`)
6. **리포트 계층**: PDF 생성(`src/pdf_report.py`)

---

## 3) 엔드투엔드 데이터 흐름
아래는 실제 실행 흐름입니다.

1. 사용자가 텍스트 또는 오디오 업로드
2. 오디오는 STT로 텍스트 변환(옵션)
3. transcript를 SQLite에 저장
4. transcript를 분석(rule-based 또는 LLM)
5. transcript 임베딩 후 ChromaDB upsert
6. 보고서 요청 시, 현재 transcript 임베딩으로 유사 세션 검색
7. 검색 결과(RAG) + 분석 결과를 묶어 최종 리포트 생성
8. JSON 응답 또는 PDF 파일 다운로드

### 예시 시나리오
- 입력 텍스트: "회의에서 무시당한 느낌이 들어 화가 났고, 집에서도 불안해서 잠을 못 잤어요."
- 분석 결과 예시:
  - mood: mixed
  - risk_score: 0.35
  - conflict_factors: ["직장/업무 갈등", "가족 갈등"]
- RAG 예시:
  - 과거에 비슷한 “직장 갈등 + 불안” 세션 3건 검색
- 최종 리포트:
  - 반복 트리거: 회의 발언 무시/성과 압박
  - 개입 아이디어: 수면 위생 질문, 지지자원 매핑, 감정기록 과제 등

---

## 4) 데모 환경의 특성(중요)
이 프로젝트는 README에 명시된 것처럼 **데모/교육용**입니다.
- 개인정보 처리(암호화/마스킹/접근통제)
- 임상 책임 범위
- 오탐 대응 절차
- 감사 로그

위 항목은 실제 운영에서 반드시 보강해야 합니다.

---

## 5) 빠른 시작 명령
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

브라우저:
- UI: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`
