# chatcli/core/graph_llm.py

from chatcli.core.config import load_config
from chatcli.core.mock import mock_llm_response

def ask_llm_with_context(self, node_id, question):
    config = load_config()
    provider = config["provider"]
    model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
    print(f"[LLM] Using {provider}: {model}")
    if node_id not in self.data:
        raise ValueError("Node ID not found")
    citations = self.get_citations(node_id)
    context_parts = []
    token_limit = 1000  # configurable later
    token_count = 0
    for cid in citations:
        cited = self.data.get(cid)
        if cited:
            snippet = cited.get("response", "")[:200]
            title = cited.get("prompt", "")[:50]
            entry = f"- {title}: {snippet}"
        entry_tokens = self.estimate_tokens(entry)
        if token_count + entry_tokens <= token_limit:
            context_parts.append(entry)
            token_count += entry_tokens
        else:
            summary = self.summarize_text(snippet)
            self.data[cid]['summary'] = summary  # Save summary to node
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


def suggest_tags(graph, node_id):
    node = graph.data.get(node_id)
    if not node:
        raise ValueError("Node not found")

    prompt = (
        f"Suggest 3 to 5 useful tags for organizing the following content:\n\n"
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
