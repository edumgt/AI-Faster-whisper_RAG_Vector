from __future__ import annotations
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os

# 한글 폰트가 없다면 기본 폰트로도 생성되지만 한글이 깨질 수 있습니다.
# 폰트를 넣고 싶으면 runtime/fonts/Pretendard-Regular.ttf 같은 경로에 두고 등록하세요.
def _try_register_korean_font():
    candidates = [
        ("Pretendard", "runtime/fonts/Pretendard-Regular.ttf"),
        ("NotoSansKR", "runtime/fonts/NotoSansKR-Regular.ttf"),
    ]
    for name, path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                return name
            except Exception:
                pass
    return "Helvetica"

def build_pdf(report: Dict[str, Any], out_path: str) -> str:
    font_name = _try_register_korean_font()
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4

    x = 18 * mm
    y = height - 18 * mm
    line_h = 6.2 * mm
    c.setFont(font_name, 14)
    c.drawString(x, y, "Counseling Analysis Report (RAG)")
    y -= line_h * 1.6

    c.setFont(font_name, 10)
    meta = f"client_id: {report.get('client_id')}   session_id: {report.get('session_id')}"
    c.drawString(x, y, meta)
    y -= line_h * 1.2

    def draw_block(title: str, body: str):
        nonlocal y
        c.setFont(font_name, 11)
        c.drawString(x, y, title)
        y -= line_h
        c.setFont(font_name, 10)
        # basic wrapping
        max_chars = 95
        for raw_line in (body or "").splitlines():
            line = raw_line.strip()
            if not line:
                y -= line_h * 0.7
                continue
            while len(line) > max_chars:
                c.drawString(x, y, line[:max_chars])
                line = line[max_chars:]
                y -= line_h
                if y < 20 * mm:
                    c.showPage()
                    y = height - 18 * mm
                    c.setFont(font_name, 10)
            c.drawString(x, y, line)
            y -= line_h
            if y < 20 * mm:
                c.showPage()
                y = height - 18 * mm
                c.setFont(font_name, 10)
        y -= line_h * 0.6

    analysis = report.get("analysis", {})
    draw_block("Transcript", report.get("transcript", ""))

    draw_block("Analysis (JSON)", str(analysis))

    rag_hits = report.get("rag_hits", [])
    rag_text = ""
    for h in rag_hits:
        rag_text += f"- score={h.get('score'):.4f} session_id={h.get('session_id')}\n  {h.get('snippet')}\n"
    draw_block("RAG Hits", rag_text or "(none)")

    final = report.get("final_report") or "(LLM disabled or failed)"
    draw_block("Final Report", final)

    c.save()
    return out_path
