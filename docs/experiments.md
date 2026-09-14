# Experiment Log

The workbench treats every retrieval improvement as an experiment against a baseline.

## Baseline: section-aware lexical retrieval

Command:

```bash
uv run rag-workbench --db demo.db ingest data/handbook.md
uv run rag-workbench --db demo.db evaluate data/evaluation.json --k 5
```

Initial sample-corpus result:

| Metric | Result |
|---|---:|
| Questions | 3 |
| Precision@5 | 0.4667 |
| Recall@5 | 1.0000 |
| Mean reciprocal rank | 1.0000 |

The baseline finds the relevant document and ranks it first for every sample question. Its
precision is lower because the corpus is small and the top-k window includes additional chunks.
That is a useful signal for the next experiment: reduce irrelevant evidence without hurting
recall.

## Experiment template

For each change, record:

1. The hypothesis
2. The implementation change
3. Retrieval metrics before and after
4. Latency and cost impact
5. Examples of improved and regressed questions

## Planned comparisons

- Baseline FTS5 vs dense embeddings
- Dense retrieval vs hybrid rank fusion
- Fixed chunks vs contextualized chunks
- Top-k retrieval vs reranked top-k
- Retrieval metrics vs grounded-answer metrics
