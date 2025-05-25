# chatcli — Modular AI Research Assistant (CLI)

**chatcli** is a modular, extensible command-line tool designed to support AI-assisted research, writing, and document management. It enables structured, hierarchical, and citation-aware conversations with support for external documents, web results, and document versioning.

---

## Features

- **Hierarchical & DAG Conversations**  
  Organize threads and sub-threads with links between topics.

- **Document Workflows**  
  Import, improve, version, and diff `.md`, `.rst`, or `.txt` documents — with Git integration.

- **Web and Citation Integration**  
  Save and cite web results, mock search or connect to Tavily/OpenAI.

- **Retrieval-Augmented Generation (RAG)**  
  Ask LLMs (mocked or real) questions using citations as context.

- **Graph Export & Visualization**  
  Export Mermaid DAGs and render SVGs of your knowledge structure.

---

## Project Structure

```
chatcli/
├── main.py              # CLI entrypoint (Typer)
├── commands/            # Modular subcommand groups
│   ├── chat.py          # Threaded conversation & DAG
│   ├── docs.py          # Document IO and versioning
│   ├── search.py        # Tag/full-text search
│   ├── web.py           # Web search + citation
│   └── export.py        # Graph visualization exports
├── core/
│   ├── graph.py         # DAG + storage logic
├── data/                # Session and document files
```

---

## Installation

```bash
pip install typer rich
git clone <this repo>
cd chatcli
```

Optional:
```bash
npm install -g @mermaid-js/mermaid-cli
```

---

## Usage

### Launch CLI
```bash
python -m chatcli.main
```

### Conversation
```bash
chatcli chat new "What's Halide?"
chatcli chat reply "And what about Tiramisu?"
chatcli chat view
chatcli chat tree
```

### Document Editing
```bash
chatcli docs import-doc design.md
chatcli docs improve-doc
chatcli docs save-doc design_v2.md
chatcli docs version-doc
chatcli docs diff-doc abc123 def456
```

### Web + RAG
```bash
chatcli web websearch "polyhedral DSLs"
chatcli web save-url 0
chatcli chat cite def456
chatcli chat ask-llm "Which DSL is more dynamic?"
```

### Search + Export
```bash
chatcli search search halide
chatcli export export-version-graph versions.mmd
chatcli export render-svg versions.mmd versions.svg
```

---

## Configuration Notes

- Git must be initialized for versioning:
```bash
git init
```

- Mermaid CLI for SVG export:
```bash
npm install -g @mermaid-js/mermaid-cli
```

---

## Extending

- Add commands under `chatcli/commands/`
- Use `graph.py` from `chatcli.core` to access and modify the DAG
- Add new types of nodes (e.g. PDF, vector-embedded docs)
- Replace mocked LLM with real OpenAI/Claude

---

## License

MIT (for your personal use)