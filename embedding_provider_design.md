
# Embedding Provider Design and Integration

## 📌 Overview
This document captures the design discussion around integrating real embedding functionality into the Conch Sage research assistant. It covers three main areas:

1. Embedding backend **options**
2. Relationship between `LLMProvider` and `EmbeddingProvider`
3. Comparative analysis of embedding **providers** based on pricing, performance, and compatibility

---

## 🔍 1. Embedding Backend Options

The original system used a mock embedding vector (`[0.1] * 768`). To support real semantic search, we now plan to use a pluggable `EmbeddingProvider` interface.

### Options:

- **OpenAI Embeddings** (`text-embedding-3-small`, etc.)
- **AWS Bedrock** (Titan Text Embeddings)
- **Claude/Anthropic** (no dedicated embedding API yet)
- **Sentence-Transformers** (local, Hugging Face models)
- **Cohere Embed API** (cloud-based)
- **Hugging Face Inference API**
- **Ollama** (⚠️ currently does not support embeddings)

---

## 🧩 2. LLMProvider vs. EmbeddingProvider

### 🧠 Conceptual Separation
| Component          | Purpose                                | Example Backends                   |
|-------------------|----------------------------------------|------------------------------------|
| `LLMProvider`     | Generates completions, chat, summaries | `OpenAI`, `Claude`, `Ollama`       |
| `EmbeddingProvider` | Converts text to dense vectors          | `OpenAI`, `Titan`, `MiniLM`        |

### ✅ Recommended Design: Keep Them Separate
- Clean separation of concerns
- Each has its own configuration section
- `ConversationGraph` exposes:

```python
get_llm() -> LLMProvider
get_embedding_provider() -> EmbeddingProvider
```

### Alternatives Considered
- **Embedding as method of LLMProvider**: breaks abstraction, not all LLMs embed
- **Unified Provider**: over-complicated, tight coupling

---

## 📊 3. Embedding Provider Comparison

| Provider                   | Quality | Latency | Cost                     | Offline | Notes                          |
|---------------------------|---------|---------|--------------------------|---------|---------------------------------|
| OpenAI (`text-embedding`) | 🔥 High | ⚡ Fast  | $0.0001–0.00013 / 1K tokens | ❌      | Best accuracy, cloud only     |
| AWS Titan (Bedrock)       | ✅ Good | ⚠️ Medium | Bedrock pricing          | ❌      | AWS-focused workflows         |
| Claude (Bedrock)          | 🟡 Fair | ⚠️ Medium | N/A                      | ❌      | No public embedding API       |
| Sentence-Transformers     | ✅ Good | ⚡ Fast  | Free (local)             | ✅      | Best for offline use          |
| Cohere Embed              | ✅ Good | ⚡ Fast  | Free tier + paid         | ❌      | Cloud-based alternative       |
| HF Inference API          | ✅ Good | ⚠️ Medium | Free tier + paid         | ❌      | Easy to swap models           |
| Ollama                    | ❌ None | —       | —                        | ✅      | No embedding support          |

### Compatibility Notes

| LLM Provider | Suggested Embedding Backend |
|--------------|-----------------------------|
| OpenAI       | OpenAI                      |
| Ollama       | Sentence-Transformers       |
| Claude       | Titan, or external          |
| Mock         | MockEmbeddingProvider       |

---

## 🧭 Recommendation by Use Case

### ✅ If you want the best quality and already use OpenAI
Use `text-embedding-3-small` or `text-embedding-ada-002`.

```yaml
embedding:
  provider: openai
  model: text-embedding-3-small
```

### ✅ If you need full offline/local capability
Use `sentence-transformers`, e.g., `all-MiniLM-L6-v2` or `bge-small-en`.

```yaml
embedding:
  provider: sentence-transformers
  model: all-MiniLM-L6-v2
```

### ✅ If you're deeply integrated with AWS
Use **Titan Embeddings** via Bedrock (if supported in your region/account).

```yaml
embedding:
  provider: bedrock
  model: amazon.titan-embed-text-v1
```

### 🧪 Experimental Setup
Support per-node or per-session embedding backend overrides to compare results side-by-side.

---

## ✅ Implementation Plan

Start with `sentence-transformers` for local support. Then optionally add OpenAI and Bedrock.

```yaml
embedding:
  provider: sentence-transformers
  model: all-MiniLM-L6-v2
```
