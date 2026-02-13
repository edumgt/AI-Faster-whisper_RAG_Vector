# Chapter 02. FastAPI 백엔드와 API 엔드포인트

## 1) 앱 엔트리포인트
`api/main.py`는 FastAPI 앱을 생성하고,
- CORS 허용
- 라우터 등록
- `/`에서 프론트 HTML 파일 반환
을 수행합니다.

즉, API 서버가 **백엔드 + 정적 프론트 진입점** 역할을 동시에 수행합니다.

---

## 2) 주요 엔드포인트 상세
`api/routes.py` 기준으로 핵심 엔드포인트는 다음과 같습니다.

### (1) `POST /seed`
샘플 파일(`samples/seed_sessions.jsonl`)을 읽어서 ingest를 반복 실행합니다.

#### 사용 예시
```bash
curl -X POST http://localhost:8000/seed
```

#### 기대 응답 예시
```json
{"ok": true, "seeded": 12}
```

---

### (2) `POST /ingest/text`
텍스트 상담을 직접 입력합니다.

#### 요청 예시
```bash
curl -X POST "http://localhost:8000/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{"client_id":"C001","transcript":"요즘 회사에서 불안하고 잠이 잘 안 옵니다."}'
```

#### 응답 예시
```json
{"ok": true, "session_id": "3ab91f7a0b1c"}
```

---

### (3) `POST /ingest/audio`
오디오 파일 업로드 후 STT 수행(옵션 패키지 필요).

#### 요청 예시
```bash
curl -X POST "http://localhost:8000/ingest/audio" \
  -F "client_id=C001" \
  -F "language=ko" \
  -F "audio=@./sample.wav"
```

#### 주의사항
- `faster-whisper` 미설치 시 400 에러 반환
- 업로드 파일은 임시 경로(`runtime/tmp`)에 저장 후 처리

---

### (4) `GET /report`
세션의 분석 + RAG 결과를 포함한 JSON 리포트를 반환합니다.

#### 요청 예시
```bash
curl "http://localhost:8000/report?client_id=C001&session_id=3ab91f7a0b1c"
```

---

### (5) `GET /report/pdf`
동일 리포트를 PDF 파일로 생성/다운로드합니다.

#### 요청 예시
```bash
curl -L "http://localhost:8000/report/pdf?client_id=C001&session_id=3ab91f7a0b1c" -o report.pdf
```

---

## 3) 에러 처리 패턴
- 샘플 파일 없으면 `HTTPException(400)`
- STT 모듈 로딩 실패 시 `HTTPException(400)`
- 리포트 생성 내부 예외를 catch하여 `HTTPException(400)`으로 전달

개발 시에는 상세 로그를 남기고, 운영에서는 사용자 메시지를 더 안전하게 제한하는 것이 바람직합니다.
