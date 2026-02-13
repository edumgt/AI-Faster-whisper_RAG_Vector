# Chapter 03. 설정 관리와 환경변수 전략

## 1) 설정 클래스 개요
`src/config.py`의 `Settings`(dataclass)는 앱의 동작 모드를 제어합니다.
`python-dotenv`로 `.env`를 자동 로드하며 주요 축은 아래와 같습니다.

- `LLM_PROVIDER`: `none|openai|ollama`
- `EMBED_PROVIDER`: `sentence-transformers|openai`
- OpenAI 관련 키/모델
- Ollama URL/모델
- RAG 검색 개수(`RAG_TOP_K`)
- 런타임 경로(`RUNTIME_DIR`, `DB_PATH`, `CHROMA_DIR`)

---

## 2) 환경별 추천 구성

### 로컬 최소 실행(외부 API 없이)
```bash
export LLM_PROVIDER=none
export EMBED_PROVIDER=sentence-transformers
```
- 장점: 빠르게 재현 가능
- 단점: 분석/리포트 품질은 규칙 기반 한계 존재

### OpenAI 기반 고품질 모드
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=...
export OPENAI_MODEL=gpt-4o-mini
export EMBED_PROVIDER=openai
export OPENAI_EMBED_MODEL=text-embedding-3-small
```
- 장점: 문장 이해력/요약 품질 향상
- 단점: 비용/네트워크 의존성

### 온프레미스 지향(Ollama)
```bash
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.1
```
- 장점: 로컬 운영 가능
- 단점: 모델/하드웨어 셋업 필요

---

## 3) 운영 팁
1. `.env`에 비밀키 저장, git 커밋 금지
2. 모델명/타임아웃을 환경별로 분리
3. `RUNTIME_DIR`를 스토리지 정책에 맞게 분리(예: `/data/app/runtime`)
4. `RAG_TOP_K`는 검색 품질과 비용(토큰량) 균형을 보며 조정

---

## 4) 예시 `.env`
```dotenv
LLM_PROVIDER=none
EMBED_PROVIDER=sentence-transformers
ST_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_TOP_K=4
RUNTIME_DIR=runtime
```
