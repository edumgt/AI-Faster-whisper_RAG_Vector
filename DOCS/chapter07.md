# Chapter 07. RAG와 벡터 검색(ChromaDB)

## 1) 저장 전략
RAG는 `src/vectordb.py`의 Chroma 컬렉션(`counseling_sessions`)을 사용합니다.
각 세션은 다음으로 저장됩니다.
- id: `session_id`
- embedding: transcript 임베딩
- document: 원문 transcript
- metadata: `client_id`, `created_at`, `source`

---

## 2) 검색 전략
`rag_search()`(`src/app_core.py`)는
1. 현재 transcript 임베딩 생성
2. `where={"client_id": client_id}` 필터로 같은 내담자 범위 제한
3. `top_k` 검색
4. distance를 score로 변환: `1 / (1 + distance)`

이렇게 하여 사용자가 이해하기 쉬운 유사도 점수 형태를 제공합니다.

---

## 3) 프롬프트 컨텍스트 구성
`src/rag.py`의 `format_hits_for_prompt()`는 검색 결과를 사람이 읽는 형식으로 합쳐, 최종 리포트 프롬프트에 삽입합니다.

예시:
```text
[1] session_id=a1b2c3 score=0.8123
회의 중 발언이 무시당해 분노가 커졌고...
```

---

## 4) 운영 시 튜닝 포인트
1. `RAG_TOP_K`: 너무 크면 노이즈 증가, 너무 작으면 회상 부족
2. 임베딩 모델 변경: 한국어 성능 비교 필요
3. 메타데이터 필터 확장(기간, source, 위험도 범주)
4. 오래된 세션 decay(가중치 감소) 고려

---

## 5) 흔한 실수
- 서로 다른 임베딩 모델로 인덱스/쿼리를 섞어 사용
- client 필터 없이 전체 검색하여 개인 맥락 오염
- 너무 긴 snippet을 그대로 프롬프트에 넣어 토큰 낭비
