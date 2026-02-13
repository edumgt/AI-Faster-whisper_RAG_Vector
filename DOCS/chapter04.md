# Chapter 04. 데이터 모델(Pydantic)과 검증 전략

## 1) 스키마 파일 구조
`src/schemas.py`는 API 입출력의 계약(Contract)을 정의합니다.

- `IngestTextIn`: 입력 payload 검증
- `AnalysisResult`: 분석 표준 구조
- `RagHit`: 유사사례 검색 단위
- `ReportOut`: 최종 보고서 응답

---

## 2) 핵심 검증 포인트

### `IngestTextIn`
- `client_id`, `transcript` 모두 최소 길이 1
- 빈 문자열 차단

### `AnalysisResult`
- `mood`는 지정 literal만 허용
- `risk_score`, `confidence`는 0.0~1.0 범위 강제

이 방식 덕분에 LLM 응답이나 내부 연산값이 이상해도, API 단에서 **형식 안정성**을 확보할 수 있습니다.

---

## 3) 왜 중요한가?
상담 도메인에서는 응답 형식 일관성이 매우 중요합니다.
예를 들어 프론트가 `risk_score`를 게이지로 렌더링할 때 문자열이 오면 UI가 깨질 수 있습니다.
Pydantic으로 사전에 막으면 유지보수 비용이 크게 줄어듭니다.

---

## 4) 실전 예시

### 잘못된 입력
```json
{"client_id":"", "transcript":"..."}
```
→ 422 Validation Error

### 잘못된 분석 출력(LLM 오작동)
```json
{"risk_score": 1.8}
```
→ `AnalysisResult.model_validate()` 단계에서 차단
