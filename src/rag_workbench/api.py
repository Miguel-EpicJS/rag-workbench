"""FastAPI surface for the RAG workbench."""

from pathlib import Path
from tempfile import gettempdir

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .service import RAGService
from .store import Store


app = FastAPI(title="RAG Workbench", version="0.1.0")
service = RAGService(Store(Path(gettempdir()) / "rag-workbench.db"))


class DocumentInput(BaseModel):
    id: str
    title: str
    text: str


class QueryInput(BaseModel):
    question: str
    limit: int = 5


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
    return service.query(request.question, min(max(request.limit, 1), 20))
