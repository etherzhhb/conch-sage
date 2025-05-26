# Conch Sage Internal Design Document

## Project Overview

**Conch Sage** is a CLI-based personal research assistant that integrates LLM workflows, semantic memory, and a graph-based conversation model. It’s designed for structured exploration, reproducible reasoning, and deep document-centric research.

---

## Architecture Summary

### Core Modules

| Module          | Purpose                                        |
|-----------------|------------------------------------------------|
| `graph.py`      | Manages DAG of nodes, citations, metadata      |
| `shell.py`      | Interactive REPL with `cmd` and prompt_toolkit |
| `main.py`       | CLI launcher (`conch-sage`)                    |
| `web.py` (mock) | Mock Tavily-style web results                  |
| `faiss` backend | Embedding + semantic search index              |

---

## Key Features

### 🌿 Graph Engine
- Nodes with prompts/responses, tags, summaries
- Parent/child and citation edges
- Full-text and tag-based search
- Tree view, backtracking, jump navigation

### 🧠 LLM Workflows
- `smart-ask`: RAG-style prompt generation from semantically matched nodes
- `smart-cite`: semantic citation suggestions
- `promote-smart-ask`: convert smart-ask into node
- `cite-smart-ask`: citation edge reconstruction

### 📄 Document Support
- Markdown/RST import
- Git-tracked versioning and inline diffing
- Subtree summarization

### 🔍 Embedding + Search
- FAISS-based simsearch with `embed-*` commands
- Embedding preview (`embed-summary`)
- `--dry-run` and `top-k` options for control

---

## CLI Interface

- REPL with history, paging, fuzzy input (prompt_toolkit)
- Modular command set: `new`, `reply`, `goto`, `view`, `tree`, `embed-node`, `simsearch`, etc.
- Persistent graph store with autosave/load

---

## Testing + CI

- `pytest` suite:
  - Core graph ops
  - Smart workflows
  - Shell simulation
  - Document diff and import
- `pytest-cov` for coverage
- GitHub Actions workflows:
  - `test.yml` (push)
  - `pr-check.yml` (pull_request)
- Codecov integration planned

---

## Project Metadata

- Name: `conch-sage`
- CLI entry point: `conch-sage`
- GitHub repo: `etherzhhb/conch-sage`
- Packaging: `setup.py`, `pyproject.toml`, `requirements.txt`
- CI: ✅ test + PR badge, ⏳ Codecov

---

## Roadmap

- [ ] `smart-thread`: automate smart-ask → promote → cite
- [ ] `reuse`, `edit-prompt` commands
- [ ] `describe-node`, `show-tags`, `show-citations`
- [ ] LLM/embedding backend toggling (OpenAI vs Bedrock)
- [ ] Graph export improvements
- [ ] PyPI packaging (optional)

---

## Summary

Conch Sage is a powerful, structured research environment in terminal form. It blends semantic memory, reproducibility, and prompt engineering into a usable tool for anyone working deeply with ideas.

### 🔁 Citation Edge Semantics (📎)

- `add_citation(from_node_id, to_node_id)` adds a **directed edge** representing:  
  “**from_node** references or depends on **to_node**.”

- Citation edges are stored in `from_node["citations"]`.

- This reflects RAG-style flows, where one node builds on or synthesizes others.

- When `auto_embed` is enabled, `from_node` is **re-embedded** to reflect the updated semantic context (now referencing `to_node`).

- `to_node` is left unchanged — it remains static as the source being cited.
- 