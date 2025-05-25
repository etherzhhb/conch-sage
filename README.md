# Conch Sage

![Test Status](https://github.com/etherzhhb/Conch Sage/actions/workflows/test.yml/badge.svg)


`Conch Sage` is a command-line personal research assistant with LLM-backed smart workflows and semantic memory.

## Features

- DAG-based hierarchical conversations
- Citation-aware semantic search
- Document import, versioning, diffing
- RAG-style `smart-ask` workflows
- FAISS-based embedding and vector search
- Interactive REPL with autocomplete and paging

## Installation

```bash
pip install -e .
```

## Running

```bash
python -m Conch Sage.shell
```

## Testing

```bash
pip install -r requirements.txt
pytest tests/
```

## Continuous Integration

This project includes GitHub Actions CI (`.github/workflows/test.yml`) which runs all tests on push and PR.

## License

MIT