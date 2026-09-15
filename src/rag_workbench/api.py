"""FastAPI surface for the RAG workbench."""

import os
from pathlib import Path
from tempfile import gettempdir

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .service import RAGService
from .store import Store

app = FastAPI(title="RAG Workbench", version="0.1.0")
database_path = Path(os.getenv("RAG_DB_PATH", Path(gettempdir()) / "rag-workbench.db"))
service = RAGService(Store(database_path))
WEB_DIR = Path(os.getenv("RAG_WEB_DIR", Path(__file__).resolve().parents[2] / "web"))


class DocumentInput(BaseModel):
    id: str
    title: str
    text: str


class QueryInput(BaseModel):
    question: str
    limit: int = 5
    mode: str = "lexical"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", **service.store.count()}


@app.post("/documents")
def add_document(document: DocumentInput) -> dict:
    chunks = service.store.add_document(document.id, document.title, document.text)
    return {"document_id": document.id, "chunks": chunks}


@app.post("/query")
def query(request: QueryInput) -> dict:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    return service.query(request.question, min(max(request.limit, 1), 20), request.mode)


@app.post("/compare")
def compare(request: QueryInput) -> dict:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    return service.compare(request.question, min(max(request.limit, 1), 20))


if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
