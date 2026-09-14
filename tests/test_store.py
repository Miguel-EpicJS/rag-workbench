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
