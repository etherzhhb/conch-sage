# 📜 Conch Sage: Internal Design Summary

## 🚀 Project Scope

**Conch Sage** is a personal-use, CLI-based AI research assistant that models conversation as a **hierarchical directed acyclic graph (DAG)** — supporting:

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

## 🌀 System Architecture Diagram

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
|  - conversations.json   |
|  - import/export (md)   |
|  - git diff/versioning  |
+-------------------------+
```

---

## 🔍 Example CLI Sessions

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
