"""Application service shared by the CLI and HTTP API."""

from pathlib import Path

from .generator import generate_answer
from .store import Store


class RAGService:
    def __init__(self, store: Store) -> None:
        self.store = store

    def ingest_file(self, path: str | Path) -> dict:
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        chunks = self.store.add_document(file_path.stem, file_path.name, text)
        return {"document_id": file_path.stem, "title": file_path.name, "chunks": chunks}

    def query(self, question: str, limit: int = 5) -> dict:
        evidence = self.store.search(question, limit)
        return {
            "question": question,
            "answer": generate_answer(question, evidence),
            "evidence": evidence,
            "retrieved": len(evidence),
        }
