from rag_workbench.generator import generate_answer


def test_baseline_answer_is_explicitly_extractive():
    answer = generate_answer(
        "What is required before deployment?",
        [{"text": "A passing test suite is required. A rollback plan is also required."}],
    )
    assert answer == "Baseline mode: A passing test suite is required."


def test_baseline_answer_handles_missing_evidence():
    assert generate_answer("unknown", []) == "Baseline mode: no matching evidence was found."
