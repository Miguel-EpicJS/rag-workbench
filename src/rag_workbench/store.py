"""SQLite persistence and full-text retrieval."""

import json
import sqlite3
from pathlib import Path


class Store:
    def __init__(self, path: str | Path = "rag-workbench.db") -> None:
        self.path = str(path)
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                section TEXT NOT NULL,
                position INTEGER NOT NULL,
                text TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS chunk_search USING fts5(
                text, title, section, content='chunks', content_rowid='id'
            );
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def add_document(self, document_id: str, title: str, text: str, metadata: dict | None = None) -> int:
        self.connection.execute(
            "INSERT OR REPLACE INTO documents(id, title, text, metadata) VALUES (?, ?, ?, ?)",
            (document_id, title, text, json.dumps(metadata or {})),
        )
        self.connection.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        chunks = self.connection.execute(
            "SELECT rowid FROM chunk_search WHERE rowid NOT IN (SELECT id FROM chunks)"
        ).fetchall()
        for row in chunks:
            self.connection.execute("DELETE FROM chunk_search WHERE rowid = ?", (row[0],))

        from .chunking import chunk_document

        created = chunk_document(document_id, title, text)
        for chunk in created:
            cursor = self.connection.execute(
                "INSERT INTO chunks(document_id, title, section, position, text) VALUES (?, ?, ?, ?, ?)",
                (chunk.document_id, chunk.document_title, chunk.section, chunk.position, chunk.text),
            )
            self.connection.execute(
                "INSERT INTO chunk_search(rowid, text, title, section) VALUES (?, ?, ?, ?)",
                (cursor.lastrowid, chunk.text, chunk.document_title, chunk.section),
            )
        self.connection.commit()
        return len(created)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        if not query.strip():
            return []
        safe_query = " OR ".join(f'"{token}"' for token in query.split() if token.strip())
        rows = self.connection.execute(
            """
            SELECT chunks.id, chunks.document_id, chunks.title, chunks.section,
                   chunks.position, chunks.text, bm25(chunk_search) AS rank
            FROM chunk_search JOIN chunks ON chunks.id = chunk_search.rowid
            WHERE chunk_search MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (safe_query, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def count(self) -> dict[str, int]:
        return {
            "documents": self.connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
            "chunks": self.connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0],
        }
