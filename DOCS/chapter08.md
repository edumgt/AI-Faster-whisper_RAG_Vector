# Chapter 08. 임베딩/LLM 계층(OpenAI, Ollama, Sentence-Transformers)

## 1) 임베딩 추상화
`src/embeddings.py`는 `EmbedderBase` 인터페이스로 제공자를 추상화합니다.

- `SentenceTransformerEmbedder`
  - 로컬 모델 인퍼런스
  - `normalize_embeddings=True`로 코사인 유사도 친화
- `OpenAIEmbedder`
  - OpenAI Embedding API 사용

`app_core.make_embedder()`가 환경변수에 따라 구현체를 선택합니다.

---

## 2) LLM 추상화
`src/llm.py`는 공통 인터페이스(`LLMBase`)를 제공합니다.
- `chat_text(system, user)`
- `chat_json(system, user, schema_hint)`

구현체:
- `OllamaLLM`: `/api/chat` REST 호출
- `OpenAILLM`: `chat.completions.create` 호출

---

## 3) JSON 출력 안정화 패턴
LLM JSON 응답은 흔히 코드블록/설명문이 섞입니다.
현재 코드는 `strip("```")` 후 `json.loads`를 시도합니다.

실무적으로는 다음 보강이 좋습니다.
1. 강력한 JSON mode 또는 schema response 사용
2. 파싱 실패 재시도(retry with repair prompt)
3. 파싱 실패 시 rule-based fallback 유지

---

## 4) 예시: OpenAI 모드 설정
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini
export EMBED_PROVIDER=openai
export OPENAI_EMBED_MODEL=text-embedding-3-small
```

이후 ingest/report 호출은 동일하며, 내부 품질만 향상됩니다.
