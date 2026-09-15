from rag_workbench.store import Store


def test_store_ingests_and_retrieves_evidence(tmp_path):
    store = Store(tmp_path / "test.db")
    try:
        count = store.add_document(
            "handbook", "Engineering Handbook", "# Deployments\nProduction deployments require a rollback plan."
        )
        results = store.search("rollback plan")
        assert count == 1
        assert results[0]["section"] == "Deployments"
        assert "rollback" in results[0]["text"]
        assert results[0]["context"].startswith("Document: Engineering Handbook")
    finally:
        store.close()


def test_replacing_document_does_not_duplicate_chunks(tmp_path):
    store = Store(tmp_path / "test.db")
    try:
        store.add_document("doc", "Doc", "# A\nold text")
        store.add_document("doc", "Doc", "# A\nnew text")
        assert store.count() == {"documents": 1, "chunks": 1}
        assert store.search("new text")[0]["text"] == "new text"
    finally:
        store.close()


def test_store_supports_dense_hybrid_and_rerank_modes(tmp_path):
    store = Store(tmp_path / "test.db")
    try:
        store.add_document("deploy", "Deployments", "# Release\nUse a rollback plan before deploy.")
        store.add_document("security", "Security", "# Access\nUse multi-factor authentication.")
        for mode in ("dense", "hybrid", "rerank"):
            results = store.search("rollback deploy", mode=mode)
            assert results
            assert results[0]["document_id"] == "deploy"
            assert results[0]["method"] == mode
    finally:
        store.close()
