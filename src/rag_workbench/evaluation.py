"""Small retrieval metrics that make baseline comparisons repeatable."""

from dataclasses import dataclass
import json
from pathlib import Path

from .store import Store


@dataclass(frozen=True)
class EvaluationResult:
    questions: int
    precision_at_k: float
    recall_at_k: float
    mean_reciprocal_rank: float

    def as_dict(self) -> dict[str, int | float]:
        return {
            "questions": self.questions,
            "precision_at_k": round(self.precision_at_k, 4),
            "recall_at_k": round(self.recall_at_k, 4),
            "mean_reciprocal_rank": round(self.mean_reciprocal_rank, 4),
        }


def evaluate(store: Store, dataset_path: str | Path, k: int = 5) -> EvaluationResult:
    """Evaluate document-level retrieval against a JSON question set."""
    if k <= 0:
        raise ValueError("k must be positive")
    examples = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    if not examples:
        raise ValueError("evaluation dataset cannot be empty")

    precisions: list[float] = []
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    for example in examples:
        expected = set(example["relevant_documents"])
        results = store.search(example["question"], k)
        retrieved = [item["document_id"] for item in results]
        hits = [document_id for document_id in retrieved if document_id in expected]
        precisions.append(len(hits) / k)
        recalls.append(len(set(hits)) / len(expected))
        reciprocal_ranks.append(1 / (retrieved.index(hits[0]) + 1) if hits else 0)

    return EvaluationResult(
        questions=len(examples),
        precision_at_k=sum(precisions) / len(precisions),
        recall_at_k=sum(recalls) / len(recalls),
        mean_reciprocal_rank=sum(reciprocal_ranks) / len(reciprocal_ranks),
    )
