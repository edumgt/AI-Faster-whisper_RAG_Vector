# 멀티모달 상담 분석 + RAG (FastAPI + Tailwind UI)

이 프로젝트는 상담 데이터를 수집/분석하고, 유사 사례를 검색(RAG)하여 최종 리포트를 생성하는 **엔드 투 엔드 파이프라인**입니다.

- 텍스트/오디오 ingest
- 심리 상태/갈등 요인/위험도 분석
- ChromaDB 기반 벡터 검색
- LLM(OpenAI/Ollama) 또는 룰 기반 fallback 리포트 생성
- PDF 리포트 다운로드
- Tailwind 기반 대시보드 UI

> ⚠️ 데모/교육용 예시입니다. 실제 서비스에서는 개인정보 보호, 임상 책임 범위, 보안/감사 로깅, 오탐 대응 절차가 반드시 필요합니다.

---

## 기술스택 도식 (Mermaid / 텍스트 기반)

아래 이미지는 이 저장소의 구성요소와 데이터 흐름을 도식화한 결과입니다.

```mermaid
flowchart LR
    A[Frontend<br/>Tailwind Dashboard] --> B[FastAPI Router]
    B --> C[Ingest Text / Audio]
    C --> D[STT faster-whisper (optional)]
    C --> E[Analysis Engine<br/>Rule-based + LLM(optional)]
    E --> F[RAG Retriever]
    F --> G[ChromaDB Vector Store]
    E --> H[SQLite Metadata/Session DB]
    E --> I[Report Generator]
    I --> J[JSON Response]
    I --> K[PDF via ReportLab]
    E --> L[OpenAI/Ollama (optional)]
```

- 위치: `docs/tech_stack.mmd`
- 특징: 바이너리 파일 없이 PR 리뷰/머지 가능한 텍스트 다이어그램

---

## 기술스택 상세

### Backend / API
- **FastAPI**: REST API 제공 (`/ingest/text`, `/ingest/audio`, `/report`, `/report/pdf`, `/seed`)
- **Uvicorn**: ASGI 서버 실행
- **Pydantic v2**: 요청/응답 스키마 검증
- **python-multipart**: 오디오 파일 업로드 처리

### AI / NLP
- **faster-whisper (옵션)**: 음성 파일 STT
- **sentence-transformers**: 임베딩 생성
- **RAG 파이프라인**: 유사 상담 문맥 검색 후 리포트 강화
- **OpenAI / Ollama (옵션)**: LLM 기반 리포트 생성

### 데이터 계층
- **SQLite**: 세션/메타데이터 저장 (`runtime/app.db`)
- **ChromaDB**: 벡터 인덱스 및 유사도 검색 (`runtime/chroma_store/`)

### 보고서/유틸리티
- **ReportLab**: PDF 생성
- **NumPy / Requests / Rich / Typer**: 수치 처리, HTTP, CLI/로그 보조

### Frontend
- **Tailwind CSS (CDN)** 기반 단일 페이지 대시보드
- 텍스트 ingest / 오디오 ingest / 리포트 조회를 한 화면에서 처리
- 다크 테마 + 카드형 레이아웃 + 반응형 구성

---

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

- UI: http://localhost:8000/
- Swagger: http://localhost:8000/docs

---

## 빠른 API 테스트

### 1) 샘플 데이터 적재
```bash
curl -X POST http://localhost:8000/seed
```

### 2) 텍스트 ingest
```bash
curl -X POST "http://localhost:8000/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{"client_id":"C001","transcript":"회의에서 무시당한 느낌이 들어 화가 났고, 집에 와서도 불안해서 잠을 잘 못 잤어요."}'
```

### 3) 리포트 생성
```bash
curl "http://localhost:8000/report?client_id=C001&session_id=<SESSION_ID>"
```

### 4) PDF 다운로드
```bash
curl -L "http://localhost:8000/report/pdf?client_id=C001&session_id=<SESSION_ID>" -o report.pdf
```

---

## 오디오 STT (옵션)

```bash
pip install faster-whisper
curl -X POST "http://localhost:8000/ingest/audio" \
  -F "client_id=C001" \
  -F "audio=@/path/to/audio.wav"
```

---

## LLM 연동 (옵션)

기본은 LLM 없이(rule-based fallback) 동작합니다.

### OpenAI
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=...
export OPENAI_MODEL=gpt-4o-mini
```

### Ollama
```bash
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.1
```

---

## 런타임 저장소

- SQLite: `./runtime/app.db`
- Chroma: `./runtime/chroma_store/`
- 임시 업로드: `./runtime/tmp/`
- PDF 결과물: `./runtime/pdf/`
