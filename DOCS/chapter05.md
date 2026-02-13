# Chapter 05. 핵심 파이프라인(app_core) 심층 분석

## 1) `ingest_transcript` 흐름
`src/app_core.py`의 `ingest_transcript`는 사실상 ingest의 메인 엔진입니다.

실행 순서:
1. 런타임 디렉터리 초기화
2. Storage/VectorStore/Embedder 생성
3. session_id 생성 및 sessions 테이블 저장
4. 분석 수행 후 analyses 테이블 저장
5. 임베딩 계산 후 Chroma upsert

즉, **메타데이터 저장 + 분석 + 벡터 인덱싱**이 한 트랜잭션 흐름으로 묶여 있습니다.

---

## 2) `build_report` 흐름
1. 세션 조회 + client_id 일치 검증
2. 저장된 분석 JSON 로드 후 스키마 검증
3. 동일 client 범위로 RAG 검색
4. LLM 활성 시 최종 리포트 생성 시도
5. 실패 시에도 기본 필드는 반환(견고한 fallback)

---

## 3) fallback 설계의 장점
- LLM 장애/네트워크 이슈 발생해도 리포트 API가 완전히 죽지 않음
- 분석 최소 기능은 rule-based로 유지 가능
- 서비스 연속성 측면에서 매우 실용적

---

## 4) 예시: LLM 실패 상황
- `LLM_PROVIDER=openai`인데 키 만료
- `build_report` 내부 `llm.chat_text()` 예외 발생
- 결과: `final_report=None`으로 응답되며 기본 분석+RAG는 유지

이 패턴은 “부분 실패 허용(Graceful Degradation)”의 대표 예시입니다.
