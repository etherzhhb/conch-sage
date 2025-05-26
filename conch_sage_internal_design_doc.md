# 📜 Conch Sage: Internal Design Summary

## 🚀 Project Scope

**Conch Sage** is a personal-use,
CLI-based AI research assistant that models conversation
as a **hierarchical directed acyclic graph (DAG)** — supporting:

* Deep, branching discussions
* Semantic citations
* Smart prompts with RAG-style context
* Version tracking, file import/export, and search

---

## ✅ High-Level System Overview

### 🧠 Core Architecture

* CLI shell using `cmd.Cmd` + `prompt_toolkit`
* Graph engine for nodes and citation edges
* Persistent storage in `conversations.json`
* Provider-agnostic support: OpenAI & AWS Bedrock
* Embedding, semantic search (FAISS), and auto-tagging

### 🔧 Key Features

* `new`, `reply`, `view`, `tree` for conversation structure
* `import_doc`, `save_doc` for external content
* `embed_*` + `simsearch` for semantic workflows
* `smart_ask`, `promote_smart_ask`, `citeurl` for RAG
* CLI autocomplete, history, and testable commands

### 🧪 Testing & DevOps

* Full `pytest` coverage with CLI test capture (`capsys`)
* GitHub Actions planned for CI
* Codecov integration planned
* Mockable embedding + LLM interface

---

# 📚 Internal Design Document

## Project Overview

**Conch Sage** is a CLI-based personal research assistant that integrates LLM workflows,
semantic memory, and a graph-based conversation model.
It’s designed for structured exploration, reproducible reasoning, and deep document-centric research.

---

## Architecture Summary

### Core Modules

| Module          | Purpose                                         |
| --------------- | ----------------------------------------------- |
| `graph.py`      | Manages DAG of nodes, citations, metadata       |
| `shell.py`      | Interactive REPL with `cmd` and prompt\_toolkit |
| `main.py`       | CLI launcher (`conch-sage`)                     |
| `web.py` (mock) | Mock Tavily-style web results                   |
| `faiss` backend | Embedding + semantic search index               |

---

## Key Features

### 🌿 Graph Engine

* Nodes with prompts/responses, tags, summaries
* Parent/child and citation edges
* Full-text and tag-based search
* Tree view, backtracking, jump navigation

### 🧠 LLM Workflows

* `smart_ask`: RAG-style prompt generation from semantically matched nodes
* `smart_cite`: semantic citation suggestions
* `promote_smart_ask`: convert smart-ask into node
* `cite_smart_ask`: citation edge reconstruction

### 📄 Document Support

* Markdown/RST import
* Git-tracked versioning and inline diffing
* Subtree summarization

### 🔍 Embedding + Search

* FAISS-based simsearch with `embed_*` commands
* Embedding preview (`embed_summary`)
* `--dry-run` and `top-k` options for control

---

## CLI Interface

* REPL with history, paging, fuzzy input (prompt\_toolkit)
* Modular command set: `new`, `reply`, `goto`, `view`, `tree`, `embed_node`, `simsearch`, etc.
* Persistent graph store with autosave/load

---

## Testing + CI

* `pytest` suite:

  * Core graph ops
  * Smart workflows
  * Shell simulation
  * Document diff and import
* `pytest-cov` for coverage
* GitHub Actions workflows:

  * `test.yml` (push)
  * `pr-check.yml` (pull\_request)
* Codecov integration planned

---

## Project Metadata

* Name: `conch-sage`
* CLI entry point: `conch-sage`
* GitHub repo: `etherzhhb/conch-sage`
* Packaging: `setup.py`, `pyproject.toml`, `requirements.txt`
* CI: ✅ test + PR badge, ⏳ Codecov

---

## Roadmap

* [ ] `smart_thread`: automate smart-ask → promote → cite
* [ ] `reuse`, `edit_prompt` commands
* [ ] `describe_node`, `show_tags`, `show_citations`
* [ ] LLM/embedding backend toggling (OpenAI vs Bedrock)
* [ ] Graph export improvements
* [ ] PyPI packaging (optional)

---

## 📊 Citation Edge Semantics (Design Detail)

* `add_citation(from_node_id, to_node_id)` adds a **directed edge** representing:
  “**from\_node** references or depends on **to\_node**.”

* Citation edges are stored in `from_node["citations"]`

* This reflects RAG-style flows, where one node builds on or synthesizes others

* When `auto_embed` is enabled, `from_node` is **re-embedded** to reflect the updated semantic context (now referencing `to_node`)

* `to_node` is left unchanged — it remains static as the source being cited

---

## Summary

Conch Sage blends structured exploration, prompt engineering,
and reproducibility into a lightweight but powerful terminal-based research tool.
It enables citation-aware thinking, graph-native prompt management,
and hybrid workflows that unify documents and LLM context.
