from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import json, uuid, tempfile

from src.config import Settings
from src.schemas import IngestTextIn, ReportOut, AnalysisResult, RagHit
from src.app_core import ingest_transcript, build_report
from src.storage import Storage
from src.pdf_report import build_pdf

router = APIRouter()

@router.post("/seed")
def seed():
    settings = Settings()
    seed_path = Path("samples/seed_sessions.jsonl")
    if not seed_path.exists():
        raise HTTPException(status_code=400, detail="samples/seed_sessions.jsonl not found")
    n = 0
    for line in seed_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        ingest_transcript(settings, row["client_id"], row["text"], source="seed")
        n += 1
    return {"ok": True, "seeded": n}

@router.post("/ingest/text")
def ingest_text(payload: IngestTextIn):
    settings = Settings()
    sid = ingest_transcript(settings, payload.client_id, payload.transcript, source="text")
    return {"ok": True, "session_id": sid}

@router.post("/ingest/audio")
def ingest_audio(
    client_id: str = Form(...),
    language: str = Form("ko"),
    audio: UploadFile = File(...),
):
    settings = Settings()

    # save temp file
    suffix = Path(audio.filename or "audio").suffix or ".wav"
    tmp_dir = Path(settings.runtime_dir) / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"upload-{uuid.uuid4().hex}{suffix}"

    with tmp_path.open("wb") as f:
        f.write(audio.file.read())

    try:
        from src.stt import transcribe_audio
    except Exception:
        raise HTTPException(status_code=400, detail="STT requires `pip install faster-whisper`")

    transcript = transcribe_audio(str(tmp_path), language=language)
    sid = ingest_transcript(settings, client_id, transcript, source="audio")
    return {"ok": True, "session_id": sid, "transcript": transcript}

@router.get("/report")
def report(client_id: str, session_id: str):
    settings = Settings()
    try:
        out = build_report(settings, client_id, session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # response_model 형태에 맞게 validate
    analysis = AnalysisResult.model_validate(out["analysis"])
    rag_hits = [RagHit.model_validate(x) for x in out.get("rag_hits", [])]
    resp = ReportOut(
        session_id=session_id,
        client_id=client_id,
        transcript=out["transcript"],
        analysis=analysis,
        rag_hits=rag_hits,
        final_report=out.get("final_report"),
    )
    return resp.model_dump()

@router.get("/report/pdf")
def report_pdf(client_id: str, session_id: str):
    settings = Settings()
    try:
        out = build_report(settings, client_id, session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    pdf_dir = Path(settings.runtime_dir) / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / f"report-{client_id}-{session_id}.pdf"
    build_pdf(out, str(pdf_path))

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )
