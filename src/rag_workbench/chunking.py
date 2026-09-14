"""Small, deterministic chunking primitives for the first RAG baseline."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    text: str
    document_id: str
    document_title: str
    section: str
    position: int


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown-like text while retaining the nearest heading as context."""
    sections: list[tuple[str, str]] = []
    heading = "General"
    body: list[str] = []

    def flush() -> None:
        content = " ".join(line.strip() for line in body if line.strip())
        if content:
            sections.append((heading, content))

    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+)$", line.strip())
        if match:
            flush()
            heading = match.group(1).strip()
            body = []
        else:
            body.append(line)
    flush()
    return sections


def chunk_document(
    document_id: str,
    title: str,
    text: str,
    max_words: int = 90,
    overlap: int = 15,
) -> list[Chunk]:
    """Create overlapping chunks without separating them from their section."""
    if max_words <= 0 or overlap < 0 or overlap >= max_words:
        raise ValueError("max_words must be positive and overlap must be smaller than max_words")

    chunks: list[Chunk] = []
    position = 0
    for section, content in split_sections(text):
        words = content.split()
        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunk_text = " ".join(words[start:end])
            chunks.append(Chunk(chunk_text, document_id, title, section, position))
            position += 1
            if end == len(words):
                break
            start = end - overlap
    return chunks
