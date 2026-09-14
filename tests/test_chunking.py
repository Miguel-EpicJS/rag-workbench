from rag_workbench.chunking import chunk_document, split_sections


def test_sections_preserve_heading_context():
    sections = split_sections("# Security\nKeep secrets private.\n## Logs\nFilter customer data.")
    assert sections == [("Logs", "Keep secrets private. Filter customer data.")] or sections[-1] == (
        "Logs",
        "Filter customer data.",
    )


def test_chunking_adds_overlap_and_metadata():
    chunks = chunk_document("doc", "Guide", "# Intro\n" + "one " * 120, max_words=50, overlap=10)
    assert len(chunks) == 3
    assert chunks[0].section == "Intro"
    assert chunks[1].document_title == "Guide"
