from fastapi.testclient import TestClient


def test_compare_endpoint_returns_all_retrieval_modes(tmp_path, monkeypatch):
    monkeypatch.setenv("RAG_DB_PATH", str(tmp_path / "api.db"))
    from rag_workbench import api

    api.service.store.add_document("doc", "Guide", "# Deployments\nUse a rollback plan before deploy.")
    client = TestClient(api.app)
    response = client.post("/compare", json={"question": "rollback plan", "limit": 2})
    assert response.status_code == 200
    assert set(response.json()) == {"lexical", "dense", "hybrid", "rerank"}
    assert response.json()["hybrid"]["mode"] == "hybrid"
    api.service.store.close()
