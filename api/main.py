from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="Counseling Multimodal RAG Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def home():
    return FileResponse(Path("api/frontend/index.html"))
