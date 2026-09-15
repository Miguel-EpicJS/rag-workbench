"""Command-line interface for repeatable ingestion and retrieval experiments."""

import argparse
import json

from .evaluation import evaluate
from .service import RAGService
from .store import Store


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspectable RAG workbench")
    parser.add_argument("--db", default="rag-workbench.db")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest")
    ingest.add_argument("path")
    query = subparsers.add_parser("query")
    query.add_argument("question")
    query.add_argument("--limit", type=int, default=5)
    query.add_argument("--mode", choices=("lexical", "dense", "hybrid", "rerank"), default="lexical")
    evaluation = subparsers.add_parser("evaluate")
    evaluation.add_argument("dataset")
    evaluation.add_argument("--k", type=int, default=5)
    subparsers.add_parser("stats")
    args = parser.parse_args()

    store = Store(args.db)
    service = RAGService(store)
    try:
        if args.command == "ingest":
            output = service.ingest_file(args.path)
        elif args.command == "query":
            output = service.query(args.question, args.limit, args.mode)
        elif args.command == "evaluate":
            output = evaluate(store, args.dataset, args.k).as_dict()
        else:
            output = store.count()
        print(json.dumps(output, indent=2))
    finally:
        store.close()
