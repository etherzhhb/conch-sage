# Conch Sage User Guide

Welcome to **Conch Sage**, your CLI-based AI research assistant. This guide outlines how different types of users can leverage Conch Sage to reason, write, research, and learn effectively using hierarchical, semantic conversations.

---

## Getting Started

Launch the interactive CLI:

```
conch-sage
```

You'll be presented with a prompt:

```
chatcli> 
```

From here, you can start new topics, reply, view the tree, ask smart questions, and manage files.

---

## Roles & Responsibilities

Conch Sage is your assistant — you steer the conversation, it supports with memory, context, and retrieval.

### You (the user):

* Drive the questions and goals
* Promote meaningful insights
* Interpret results, validate facts
* Tag and organize when needed

### Conch Sage (the tool):

* Tracks structure and citations
* Embeds and retrieves semantically
* Formats smart prompts and logs context
* Persists and visualizes your thought process

---

## Core Commands

## Core Commands

| Command                      | Description                                      |
| ---------------------------- | ------------------------------------------------ |
| `new <question>`             | Start a new root-level discussion node           |
| `reply <text>`               | Reply to current node, creating a child          |
| `view`                       | View current node prompt and response            |
| `tree`                       | Show the tree from current, root, or parent      |
| `tree_all`                   | Show the full DAG from all root-level nodes      |
| `goto <node_id>`             | Jump to a different node in the DAG              |
| `parent`                     | Move to the parent of the current node           |
| `smart_ask <question>`       | Ask an LLM question using semantic RAG context   |
| `smart_ask --promote`        | Ask and automatically promote the LLM response   |
| `promote_smart_ask`          | Save the last smart\_ask as a new node           |
| `embed_node`                 | Embed the current node for semantic search       |
| `simsearch <keywords>`       | Search embedded nodes by similarity              |
| `suggest-replies`            | Suggest follow-up questions from current context |
| `suggest-tags`               | Suggest semantic tags for the current node       |
| `suggest-validation-sources` | Suggest citations or sources to validate content |
| `import_doc <path>`          | Import a markdown or RST document                |
| `export_to_file <file>`      | Export current graph (nodes + smart\_ask)        |

---

## Personas & Example Workflows

### 👨‍💼 Researcher

**Goal**: Build structured arguments, synthesize sources

```
new What are the main challenges in scheduling DSLs?
reply How does Halide solve locality?
reply How is Tiramisu different?
suggest-replies
smart_ask Compare Halide and Tiramisu --promote
add_citation from latest node to related findings
```

### 👩‍🎓 Learner

**Goal**: Learn interactively and semantically

```
new Explain diffusion models
reply What is classifier-free guidance?
import_doc stable_diffusion.md
smart_ask How is CFG implemented in the model?
suggest-validation-sources
view
tree
suggest-tags
tag current as diffusion, basics
```

### 🧑‍💼 Engineer

**Goal**: Explore and refine a system design

```
new Design a GPU async kernel abstraction
reply What is warp specialization?
import_doc design_notes.rst
embed_all
simsearch kernel
subtree_summary
```

### 🧑‍📈 Debugging Detective

**Goal**: Investigate technical failures systematically

```
new Investigate model slowdown
reply Check dataloader bottlenecks
reply Look at GPU kernel logs
smart_ask Any reasons GPU scheduling stalls?
promote_smart_ask
show-citations
```

---

## File Management

* Save session: `export_to_file design-thread.json`
* Resume: `import_from_file design-thread.json`
* Git-integrated version tracking is automatically supported.

---

## Next Steps

* Try `help` in the CLI for a full command list.
* Use `tree` and `goto` to navigate the DAG structure.
* Explore `smart_thread`, `reuse`, `subtree_summary`, `suggest-*` commands.

---

Conch Sage is built to support focused thinking, reusable prompts, semantic memory, and reproducible reasoning. Explore deeply, navigate quickly, and make your thoughts searchable.
