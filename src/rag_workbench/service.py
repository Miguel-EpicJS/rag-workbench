"""Application service shared by the CLI and HTTP API."""

from pathlib import Path

from .generator import generate_answer, validate_citations, validate_grounding
from .store import Store


class RAGService:
    def __init__(self, store: Store) -> None:
        self.store = store

    def ingest_file(self, path: str | Path) -> dict:
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        chunks = self.store.add_document(file_path.stem, file_path.name, text)
        return {"document_id": file_path.stem, "title": file_path.name, "chunks": chunks}

    def query(self, question: str, limit: int = 5, mode: str = "lexical") -> dict:
        evidence = self.store.search(question, limit, mode)
        answer = generate_answer(question, evidence)
        return {
            "question": question,
            "mode": mode,
            "answer": answer,
            "citations": validate_citations(answer, len(evidence)),
            "grounding": validate_grounding(answer, evidence),
            "evidence": evidence,
            "retrieved": len(evidence),
        }

    def compare(self, question: str, limit: int = 5) -> dict:
        return {
            mode: self.query(question, limit, mode)
            for mode in ("lexical", "dense", "hybrid", "rerank")
        }
