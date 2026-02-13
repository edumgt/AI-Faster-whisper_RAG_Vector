# Chapter 09. 저장소(SQLite/Chroma)와 리포트 PDF

## 1) SQLite 스키마
`src/storage.py`는 2개 테이블을 생성/사용합니다.

1. `sessions`
- session_id(PK), client_id, created_at, source, transcript

2. `analyses`
- session_id(PK/FK), analysis_json, created_at

`upsert_*` 메서드로 idempotent 업데이트를 지원합니다.

---

## 2) Chroma 영속화
벡터 DB는 `runtime/chroma_store/` 경로에 persist됩니다.
장점:
- 재시작 후에도 인덱스 유지
- seed 후 즉시 유사도 검색 가능

주의:
- 임베딩 모델을 바꾸면 재인덱싱 권장

---

## 3) PDF 생성 흐름
`src/pdf_report.py`의 `build_pdf()`는 ReportLab 캔버스로
- 메타 정보
- transcript
- analysis JSON
- RAG hits
- final report
를 순차 렌더링합니다.

한글 폰트는 `runtime/fonts` 경로에서 자동 탐색합니다.
- `Pretendard-Regular.ttf`
- `NotoSansKR-Regular.ttf`

없으면 Helvetica로 fallback되며 한글이 깨질 수 있습니다.

---

## 4) PDF 품질 개선 팁
1. 본문 줄바꿈을 글자 수가 아닌 폭 기반으로 개선
2. JSON pretty-print 적용
3. 위험도/감정을 표/박스로 시각화
4. 페이지 헤더/푸터(생성일, 페이지번호) 추가
