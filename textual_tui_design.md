# Conch Sage Textual TUI Design Document

## Overview

This document outlines the system design for a Textual-based TUI (Text User Interface) for Conch Sage — a DAG-based personal research assistant. The TUI aims to provide an interactive terminal interface that combines a ChatGPT-style chat experience with a structured graph-based navigation system.

---

## Goals

- Create an intuitive, chat-first interface for interacting with Conch Sage.
- Enable users to navigate and manage non-linear, hierarchical conversations (DAGs).
- Present node metadata, citations, and semantic context in a structured, accessible layout.
- Leverage existing `ConversationGraph` backend and LLM/embedding infrastructure.

---

## Architecture Overview

```
User (Keyboard/Mouse)
        │
        ▼
  ┌──────────────────────┐
  │   Textual TUI App    │
  └──────────────────────┘
        │
        ▼
+----------------------+     +--------------------------+
|   UI Controllers     | <-> | ConversationGraph Backend |
| (Chat, DAG, Node)    |     +--------------------------+
+----------------------+
        │
        ▼
+--------------------------+
| LLM & Embedding Backends |
| (OpenAI, Claude, Ollama) |
+--------------------------+
```

---

## UI Layout

```
┌──────────────────────── Chat View ────────────────────────┐
│ [User]: What is loop fusion?                              │
│ [LLM]: Loop fusion combines adjacent loops...             │
│ [User]: Give an example                                   │
│ [LLM]: Sure, here's a code snippet...                     │
└───────────────────────────────────────────────────────────┘
┌──── DAG Navigator ─────┐   ┌──── Node Info / Context ─────┐
│ Root: Loop Optimization│   │ ID: 1234abcd                │
│ ├─ Loop Fusion         │   │ Tags: optimization, loop    │
│ │  └─ Example Code     │   │ Cited by: 4 nodes           │
│ └─ Loop Tiling         │   │ Related: ...                │
└────────────────────────┘   └─────────────────────────────┘
```

---

## Core Components

### 1. `ChatPane`
- Scrollable chat history
- Text input field for user prompts
- Sends input to LLM and displays response
- Option to promote or cite response

### 2. `DAGNavigatorPane`
- Tree view of conversation graph
- Keyboard navigable
- Allows switching current context

### 3. `NodeDetailPane`
- Displays full content of selected node
- Metadata: ID, tags, citations, related nodes
- Rendered in rich markdown

### 4. `StatusBar` (optional)
- Active session, selected LLM provider, node ID
- Autosave, embedding, or mode indicators

---

## Controllers

| Controller         | Responsibility                              |
|--------------------|----------------------------------------------|
| `ChatController`   | Handles user input, response generation      |
| `GraphController`  | Manages DAG structure, session navigation    |
| `NodeController`   | Loads metadata, triggers embedding/search    |

---

## Backend Integration

- Reuse `ConversationGraph` for:
  - Node creation (`new`, `reply`)
  - Context retrieval
  - Embedding and FAISS-based `simsearch`
  - Versioning and smart-ask workflows

- Use pluggable `LLMProvider` abstraction for:
  - Local (Ollama)
  - Cloud (OpenAI, Claude)

---

## Async Design Considerations

- LLM calls and embeddings must be `async def`
- TUI will show loading state (e.g. spinner or disabled input)
- Async file I/O for document loading and save

---

## Future Enhancements

- Modal command palette (`Ctrl+P`) for global commands
- Semantic browsing and similarity-based node suggestions
- Inline citation viewer (popup or modal)
- Keyboard shortcuts for mode switching
- Export DAG as SVG or HTML for documentation

---

## Next Steps

1. Scaffold `TextualApp` with grid layout
2. Implement `ChatPane` and connect to `ConversationGraph`
3. Add `DAGNavigatorPane` with basic tree rendering
4. Connect node selection to `NodeDetailPane`
5. Wire async LLM backend into `ChatController`

---

## License

This design is part of the Conch Sage project and is licensed under the MIT License.