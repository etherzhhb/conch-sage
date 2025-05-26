# 📜 Conch Sage: Internal Design Summary

## 🚀 Project Scope

**Conch Sage** is a CLI-based, personal-use AI research assistant that models conversations as a **hierarchical directed acyclic graph (DAG)**. It supports:

* Deep, branching discussions
* Semantic citation and referencing
* Smart prompts with RAG-style context injection
* Version tracking, file diffing, and doc import/export
* Embedding-based search and tagging

---

## ✅ High-Level System Overview

### 🧠 Core Architecture

* CLI shell using `cmd.Cmd` + `prompt_toolkit`
* DAG graph engine: nodes (prompt/response/summaries), edges (hierarchy + citation)
* Persistent storage with `self._path`, no global state
* Provider-agnostic embedding support (OpenAI, Bedrock)
* FAISS-based simsearch backend

### 🔧 Key Features

* Conversation structure: `new`, `reply`, `view`, `tree`, `goto`
* Smart workflows: `smart_ask`, `promote_smart_ask`, `smart_cite`
* Document features: `import_doc`, subtree summary, git versioning, inline diff
* Embedding: `embed_node`, `embed_subtree`, `embed_summary`, `embed_all`, `simsearch`
* Web search: `mock_websearch`, `save_web_result`, `citeurl`, `smart_ask` with RAG
* Autocomplete, history, `fzf` search, fuzzy node targeting

### 🧪 Testing & DevOps

* `pytest`-based unit tests with mocks, CLI output captured via `capsys`
* Edge cases for file I/O, smart ask, citation handling, etc.
* GitHub Actions integrated for PR/test CI
* Codecov integration planned

---

## 🔄 Refactor & Internal Improvements

* Eliminated global `DATA_PATH`, `SAVE_DIR`
* Unified persistence with `_save()` / `_load(path)` using new format:

  ```json
  {
    "nodes": {...},
    "last_smart_ask": {...}
  }
  ```
* New methods: `export_to_file()`, `import_from_file()`
* Better test support via `tmp_path`, `tempfile`, custom `storage_path`

---

## 🔹 Example CLI Sessions

### New Node and Reply

```bash
chatcli> new What is loop fusion?
New node: a1b2c3d4

chatcli> reply It combines loops to improve cache locality.
Replied with node: e5f6g7h8

chatcli> view
[e5f6g7h8] It combines loops to improve cache locality.
```

### Embedding and Semantic Search

```bash
chatcli> embed_node
[Embedding] Using openai (mock)
Embedded node e5f6g7h8

chatcli> simsearch fusion
Results:
e5f6g7h8  0.89  It combines loops to improve cache locality.
```

### Smart Ask and Promote

```bash
chatcli> smart_ask What are loop transformations?
Smart response: Loop interchange, unrolling, fusion, and tiling optimize nested loops.

chatcli> promote_smart_ask
Promoted to new node: z9y8x7w6
```

---

## 📊 System Architecture Diagram

```
+-------------------------+
|      CLI Shell         |
|  (cmd + prompt_toolkit)|
+-----------+-------------+
            |
            v
+-----------+-------------+
|     Graph Engine        |
|  - Nodes & Edges (DAG) |
|  - Prompts/Responses    |
|  - Citations & Tags     |
+-----------+-------------+
            |
            v
+-----------+-------------+
|     Embedding Layer     |
|  - FAISS Index          |
|  - Provider Backends    |
|    (OpenAI / Bedrock)   |
+-----------+-------------+
            |
            v
+-----------+-------------+
|     I/O and Storage     |
|  - graph.json, exports  |
|  - subtree summary      |
|  - git version tracking |
+-------------------------+
```

---

## 🔢 Division of Responsibilities: User vs Tool

| Role                      | User Responsibilities                                       | Tool Responsibilities                                        |
| ------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------ |
| **Conversation Flow**     | Initiate topics, reply to nodes, guide discussion direction | Maintain parent/child links, current context node            |
| **Smart Questions**       | Ask meaningful `smart_ask` prompts                          | Build RAG prompts, fetch LLM responses, log smart\_ask state |
| **Citation**              | Select appropriate sources to cite                          | Track citation edges and optionally auto-embed               |
| **Navigation**            | Use `tree`, `goto`, and tags to explore                     | Store graph data and support jump/navigation commands        |
| **Embedding & Search**    | Trigger embedding or similarity search when needed          | Call embedding backend, manage FAISS index                   |
| **File/Version Handling** | Import/export docs, optionally manage Git history           | Serialize to JSON, Git diff hooks, `_save`/`_load`           |
| **Interpretation**        | Interpret and validate LLM responses                        | None (tool doesn't evaluate truth)                           |
| **Automation**            | Use helper flows like `smart_thread`                        | Automate chained steps like smart\_ask → promote → cite      |

---

## 🔍 Roadmap

* [ ] `smart_thread`: automate smart-ask → promote → cite
* [ ] CLI discoverability: `describe-node`, `show-tags`, `show-citations`
* [ ] Prompt templating via Jinja2
* [ ] Improved node targeting via fuzzy matching
* [ ] Graph export with filters, SVG/HTML
* [ ] PyPI packaging (optional)

---

## 🔍 Citation Edge Semantics

* `add_citation(from_node_id, to_node_id)` creates a **directed edge**:

  > from\_node references to\_node

* Edges are stored as `from_node['citations']`

* Used to build RAG context

* Triggers optional `auto_embed` on the citing node only

---

## 📃 Summary

**Conch Sage** is a reproducible, structured CLI environment for LLM-driven research workflows:

* DAG memory structure
* Embedding + search
* Smart prompting with traceable context
* File/document support with versioning

It is built to be personal, modular, testable, and extensible.
