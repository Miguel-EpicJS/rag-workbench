"""Deterministic dense, hybrid, and second-stage retrieval utilities."""

import hashlib
import math
import re

TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


def tokens(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def embed(text: str, dimensions: int = 128) -> list[float]:
    """Create a dependency-free hashed embedding for reproducible experiments."""
    vector = [0.0] * dimensions
    for token in tokens(text):
        digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def dense_rank(chunks: list[dict], query: str) -> list[dict]:
    query_vector = embed(query)
    ranked = []
    for chunk in chunks:
        searchable = f"{chunk['title']} {chunk['section']} {chunk['text']}"
        item = dict(chunk)
        item["score"] = cosine(query_vector, embed(searchable))
        item["method"] = "dense"
        ranked.append(item)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def reciprocal_rank_fusion(*rankings: list[dict], k: int = 60) -> list[dict]:
    """Fuse rankings while preserving a single inspectable result per chunk."""
    scores: dict[int, float] = {}
    items: dict[int, dict] = {}
    for ranking in rankings:
        for position, item in enumerate(ranking, start=1):
            chunk_id = item["id"]
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (k + position)
            items[chunk_id] = dict(item)
    result = []
    for item_id, item in scores.items():
        result_item = items[item_id]
        result_item["score"] = item
        result_item["method"] = "hybrid"
        result.append(result_item)
    return sorted(result, key=lambda item: item["score"], reverse=True)


def rerank(query: str, candidates: list[dict]) -> list[dict]:
    """Apply a transparent lexical overlap pass after broad retrieval."""
    query_terms = set(tokens(query))
    ranked = []
    for candidate in candidates:
        text_terms = set(tokens(f"{candidate['title']} {candidate['section']} {candidate['text']}"))
        overlap = len(query_terms & text_terms) / max(len(query_terms), 1)
        item = dict(candidate)
        item["score"] = overlap
        item["method"] = "rerank"
        ranked.append(item)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)
