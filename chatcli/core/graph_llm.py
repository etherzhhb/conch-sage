# chatcli/core/graph_llm.py

from chatcli.core.llm_provider import get_llm


def ask_llm_with_context(graph, node_id, question):
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
    llm = get_llm()
    return llm.ask_with_context(context, question)


def suggest_replies(graph, node_id, top_k=3):
    from chatcli.core.prompt_loader import render_template

    node = graph.data.get(node_id)
    if not node:
        raise ValueError("Node not found")

    context = node.get("response") or node.get("prompt", "")

    prompt = render_template(
        "suggest_replies.j2",
        context=context.strip(),
        top_k=top_k,
    )

    return graph.ask_llm_with_context(node_id, prompt)

def suggest_tags(graph, node_id, top_k=3):
    from chatcli.core.prompt_loader import render_template

    node = graph.data.get(node_id)
    if not node:
        raise ValueError("Node not found")

    prompt = render_template(
        "suggest_tags.j2",
        top_k=top_k,
        prompt=node.get("prompt", ""),
        response=node.get("response", ""),
    )

    return graph.ask_llm_with_context(node_id, prompt).strip()


def suggest_validation_sources(graph, node_id, top_k=3):
    from chatcli.core.prompt_loader import render_template

    node = graph.data.get(node_id)
    if not node:
        raise ValueError("Node not found")

    response = node.get("response", "")

    prompt = render_template(
        "suggest_validation_sources.j2",
        top_k=top_k,
        response=response.strip(),
    )

    return graph.ask_llm_with_context(node_id, prompt)


def ask_llm_direct(graph, prompt):
    llm = get_llm()
    return llm.ask(prompt)


def estimate_tokens(graph, text):
    # Basic token estimate: ~1 token per 4 characters (OpenAI rough rule)
    return len(text) // 4


def get_embedding(graph, text):
    provider = graph.get_embedding_provider()
    print(f"[Embedding] Using {provider.__class__.__name__}")
    return provider.embed(text)

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
