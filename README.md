# RAG Workbench

[![CI](https://github.com/Miguel-EpicJS/rag-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/Miguel-EpicJS/rag-workbench/actions/workflows/ci.yml)

An inspectable workbench for improving retrieval-augmented generation systems.

This is not another chatbot wrapper. The project makes the retrieval layer visible so each
iteration can be measured:

```text
documents -> section-aware chunks -> SQLite FTS5 -> ranked evidence -> grounded answer
```

The first release is intentionally deterministic. It creates a baseline before adding more
advanced techniques such as dense embeddings, hybrid rank fusion, contextual retrieval, and
neural reranking.

## Why this project exists

Many RAG failures are blamed on the LLM before anyone inspects the evidence sent to it. RAG
Workbench exposes the document, section, chunk position, text, and retrieval score returned for
each question. That makes it possible to turn vague quality discussions into reproducible
experiments.

## Features

- Markdown-aware section splitting
- Overlapping chunks with document and section metadata
- Local SQLite persistence with FTS5 retrieval
- Evidence-first query responses
- Optional OpenAI-compatible generation for Ollama, llama.cpp, or hosted APIs
- CLI and FastAPI interfaces
- Tests for chunking, replacement, metadata, and retrieval

## Quick start

```bash
uv sync --extra dev
uv run rag-workbench --db demo.db ingest data/handbook.md
uv run rag-workbench --db demo.db query "What is required before a production deployment?"
```

Without an LLM configured, the query command still returns the retrieved evidence. To enable
generation, point the project at an OpenAI-compatible endpoint:

```bash
export LLM_BASE_URL=http://localhost:8080/v1
export LLM_MODEL=qwen-local
uv run rag-workbench --db demo.db query "What is required before a production deployment?"
```

Start the API with:

```bash
uv run uvicorn rag_workbench.api:app --reload
```

Then ingest and query documents with JSON:

```bash
curl -X POST http://localhost:8000/documents \
  -H 'content-type: application/json' \
  -d '{"id":"handbook","title":"Engineering Handbook","text":"# Deployments\nProduction deployments require a rollback plan."}'

curl -X POST http://localhost:8000/query \
  -H 'content-type: application/json' \
  -d '{"question":"What is required for deployments?","limit":3}'
```

## Experiment roadmap

- [x] Section-aware chunking baseline
- [x] Inspectable lexical retrieval
- [x] Evidence-first API and CLI
- [x] Retrieval evaluation dataset and metrics
- [x] Continuous integration with linting and tests
- [ ] Dense embeddings and hybrid rank fusion
- [ ] Cross-encoder reranking
- [ ] Contextual chunk enrichment
- [ ] Citation validation and answer faithfulness checks
- [ ] Web UI for comparing retrieval experiments

## Development

```bash
uv sync --extra dev
uv run pytest
```

## Content series

This repository is designed to evolve in public. Each roadmap step can become a technical
write-up comparing one change against the baseline: what changed, which failures improved, and
what it cost in latency or complexity.

## License

MIT
