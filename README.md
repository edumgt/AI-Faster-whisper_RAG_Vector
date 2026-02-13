# 멀티모달 상담 분석 + RAG (FastAPI 확장 예시)

이 프로젝트는 다음 흐름을 FastAPI로 제공합니다.

- (옵션) STT: 오디오 업로드 → 텍스트 변환
- 분석: 심리 상태/갈등 요인/위험도(0~1) JSON
- Vector DB: ChromaDB(로컬 퍼시스턴트)
- RAG: 과거 유사 상담 검색 후 리포트 생성
- (옵션) PDF: 리포트를 PDF로 생성 다운로드

> ⚠️ 데모/교육용. 실제 서비스는 개인정보/보안/임상 책임 범위/오탐 대응 프로토콜이 필수입니다.

---

## 1) 설치

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

---

## 2) 실행

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger:
- http://localhost:8000/docs

---

## 3) 빠른 테스트 (curl)

### seed (샘플 상담 내역 적재)
```bash
curl -X POST http://localhost:8000/seed
```

### 텍스트 ingest
```bash
curl -X POST "http://localhost:8000/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{"client_id":"C001","transcript":"회의에서 무시당한 느낌이 들어 화가 났고, 집에 와서도 불안해서 잠을 잘 못 잤어요."}'
```

### 리포트 생성 (RAG 포함)
```bash
curl "http://localhost:8000/report?client_id=C001&session_id=<SESSION_ID>"
```

### PDF 다운로드
```bash
curl -L "http://localhost:8000/report/pdf?client_id=C001&session_id=<SESSION_ID>" -o report.pdf
```

---

## 4) 오디오 STT (옵션)

```bash
pip install faster-whisper
curl -X POST "http://localhost:8000/ingest/audio" \
  -F "client_id=C001" \
  -F "audio=@/path/to/audio.wav"
```

---

## 5) LLM 연동(옵션)

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

## 6) 런타임 저장소

- SQLite: `./runtime/app.db`
- Chroma: `./runtime/chroma_store/`
