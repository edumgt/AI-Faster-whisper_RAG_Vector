from __future__ import annotations
from typing import Optional

def transcribe_audio(audio_path: str, language: Optional[str] = "ko") -> str:
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _info = model.transcribe(audio_path, language=language, vad_filter=True)
    texts = [seg.text.strip() for seg in segments if seg.text and seg.text.strip()]
    return " ".join(texts)
