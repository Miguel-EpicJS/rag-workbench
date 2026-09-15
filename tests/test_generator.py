from rag_workbench.generator import generate_answer


def test_baseline_answer_is_explicitly_extractive():
    answer = generate_answer(
        "What is required before deployment?",
        [{"text": "A passing test suite is required. A rollback plan is also required."}],
    )
    assert answer == "Baseline mode: A passing test suite is required. [1]"


def test_baseline_answer_handles_missing_evidence():
    assert generate_answer("unknown", []) == "Baseline mode: no matching evidence was found."


def test_citations_are_checked_against_evidence():
    from rag_workbench.generator import validate_citations

    assert validate_citations("A claim [1].", 1) == {"valid": True, "references": [1]}
    assert validate_citations("A claim [2].", 1)["valid"] is False


def test_grounding_checks_answer_terms_against_evidence():
    from rag_workbench.generator import validate_grounding

    evidence = [{"text": "A rollback plan is required before deployment."}]
    assert validate_grounding("A rollback plan is required. [1]", evidence)["grounded"] is True
    assert validate_grounding("The moon is made of cheese. [1]", evidence)["grounded"] is False
