import json

from rag_workbench.evaluation import evaluate
from rag_workbench.store import Store


def test_evaluation_reports_retrieval_metrics(tmp_path):
    store = Store(tmp_path / "test.db")
    dataset = tmp_path / "evaluation.json"
    dataset.write_text(
        json.dumps([{"question": "rollback plan", "relevant_documents": ["handbook"]}]),
        encoding="utf-8",
    )
    try:
        store.add_document("handbook", "Handbook", "# Deployments\nA rollback plan is required.")
        result = evaluate(store, dataset, k=2)
        assert result.questions == 1
        assert result.recall_at_k == 1
        assert result.mean_reciprocal_rank == 1
    finally:
        store.close()
