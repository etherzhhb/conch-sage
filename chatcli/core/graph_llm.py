# chatcli/core/graph_llm.py

from chatcli.core.config import load_config
from chatcli.core.mock import mock_llm_response

def ask_llm_with_context(graph, node_id, question):
    config = load_config()
    provider = config["provider"]
    model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
    print(f"[LLM] Using {provider}: {model}")
    if node_id not in graph.data:
        raise ValueError("Node ID not found")
    citations = graph.get_citations(node_id)
    context_parts = []
    token_limit = 1000  # configurable later
    token_count = 0
    for cid in citations:
        cited = graph.data.get(cid)
        if cited:
            snippet = cited.get("response", "")[:200]
            title = cited.get("prompt", "")[:50]
            entry = f"- {title}: {snippet}"
        entry_tokens = graph.estimate_tokens(entry)
        if token_count + entry_tokens <= token_limit:
            context_parts.append(entry)
            token_count += entry_tokens
        else:
            summary = graph.summarize_text(snippet)
            graph.data[cid]['summary'] = summary  # Save summary to node
            context_parts.append(f"- {title}: {summary}")
            break
    context = "\n".join(context_parts) if context_parts else "No supporting information available."
    response = f"[MOCK LLM RESPONSE]\nUsing sources:\n{context}\n\nAnswer: {question} is a good question!"
    return response


def suggest_replies(graph, node_id, top_k=3):
    node = graph.data.get(node_id)
    if not node:
        raise ValueError("Node not found")
    context = node.get("response") or node.get("prompt")
    prompt = (
        f"Based on the following conversation:\n\n{context.strip()}\n\n"
        f"Suggest {top_k} relevant follow-up questions."
    )
    config = load_config()
    provider = config["provider"]
    model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
    print(f"[LLM] Using {provider}: {model}")
    reply = graph.ask_llm_with_context(node_id, prompt)
    return reply


def suggest_tags(graph, node_id, top_k=3):
    node = graph.data.get(node_id)
    if not node:
        raise ValueError("Node not found")

    prompt = (
        f"Suggest {top_k} useful tags for organizing the following content:\n\n"
        f"{node.get('prompt', '')}\n\n{node.get('response', '')}"
    )
    config = load_config()
    provider = config["provider"]
    model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
    print(f"[LLM] Using {provider}: {model}")
    tags_text = graph.ask_llm_with_context(node_id, prompt)
    return tags_text.strip()


def suggest_validation_sources(graph, node_id, top_k=3):
    node = graph.data.get(node_id)
    if not node:
        raise ValueError("Node not found")
    response = node.get("response", "")
    prompt = (
        f"Suggest {top_k} sources or search queries I could use to validate or fact-check this explanation:\n\n"
        f"{response.strip()}"
    )
    config = load_config()
    provider = config["provider"]
    model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
    print(f"[LLM] Using {provider}: {model}")
    return graph.ask_llm_with_context(node_id, prompt)


def ask_llm_direct(graph, prompt):
    config = load_config()
    provider = config["provider"]
    model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
    print(f"[LLM] Using {provider}: {model}")
    return mock_llm_response(prompt)


def estimate_tokens(graph, text):
    # Basic token estimate: ~1 token per 4 characters (OpenAI rough rule)
    return len(text) // 4


def get_embedding(graph, text):
    config = graph._config
    provider = config["provider"]
    print(f"[Embedding] Using {provider} (mock)")
    return [0.1] * 768  # mock vector


def embed_node(graph, node_id, dry_run=False):
    if node_id not in graph.data:
        raise ValueError("Node not found")
    node = graph.data[node_id]
    combined = f"{node.get('prompt', '')}\n{node.get('response', '')}"
    if dry_run:
        print(f"[DRY RUN] Would embed node {node_id}")
    else:
        node["embedding"] = graph.get_embedding(combined)
    graph._save()
    print(f"Embedded node {node_id}")
