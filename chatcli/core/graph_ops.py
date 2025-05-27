# chatcli/core/graph_ops.py
import faiss
import numpy as np

from chatcli.core.config import load_config

def smart_ask(graph, query_text, from_node_id=None, top_k=3):
    """
    Run a smart-ask by semantically retrieving relevant nodes and generating an LLM answer.
    This constructs a RAG-style prompt using the top-K semantically similar nodes.

    Args:
        query_text (str): The user's question.
        from_node_id (str): The context node initiating the ask.
        top_k (int): Number of similar nodes to retrieve.

    Returns:
        str: The LLM-generated answer.
    """
    matches = graph.simsearch(query_text, top_k=top_k)
    context_chunks = []
    citations = []

    for node_id, _score in matches:
        node = graph.data.get(node_id, {})
        context = node.get("response") or node.get("prompt")
        if context:
            label = f"[CONTEXT from {node_id}]"
            context_chunks.append(label + "\n" + context.strip())
            citations.append(node_id)

    full_prompt = "\n\n".join(context_chunks)
    full_prompt += "\n\n[QUESTION]\n" + query_text.strip()

    if from_node_id is None or from_node_id not in graph.data:
        answer = graph.ask_llm_direct(full_prompt)
    else:
        answer = graph.ask_llm_with_context(from_node_id, full_prompt)

    graph._last_smart_ask = {
        "from_node_id": from_node_id,
        "question": query_text.strip(),
        "response": answer,
        "citations": citations,
    }

    return answer

def promote_smart_ask(graph, parent_id: str) -> str:
    """
    Promote the most recent smart-ask result into a new graph node.

    This function takes the cached smart-ask result — including the question, generated answer,
    and any cited nodes — and creates a new child node under the given `parent_id`. It copies
    the smart-ask content into the graph and establishes citation edges from the new node to
    its cited sources. If `auto_embed` is enabled, it will also embed the new node.

    Args:
        parent_id (str): The ID of the node that initiated the smart-ask.

    Returns:
        str: The node ID of the newly created promoted smart-ask node.

    Raises:
        ValueError: If no smart-ask has been performed yet or if it doesn't match the parent.
    """
    if graph._last_smart_ask is None:
        raise ValueError("No smart-ask result available to promote.")

    data = graph._last_smart_ask
    if data["from_node_id"] != parent_id:
        raise ValueError("Smart-ask result does not match current node.")

    prompt = data["question"]
    response = data["response"]
    citations = data.get("citations", [])

    node_id = graph._generate_id()
    graph.data[node_id] = {
        "id": node_id,
        "parent_id": parent_id,
        "prompt": prompt,
        "response": response,
        "children": [],
        "tags": ["smart-ask"]
    }

    graph.data[parent_id]["children"].append(node_id)

    for cited_id in citations:
        graph.add_citation(node_id, cited_id)

    config = load_config()
    if config.get("auto_embed", False):
        graph.embed_node(node_id)

    graph._save()
    return node_id

def cite_smart_ask(graph, target_node_id=None):
    if not graph._last_smart_ask:
        raise ValueError("No smart_ask to cite")
    target = target_node_id or graph._last_smart_ask["from_node_id"]
    for cited in graph._last_smart_ask.get("citations", []):
        graph.add_citation(target, cited)


def smart_thread(graph, question, from_node_id=None, top_k=3):
    answer = graph.smart_ask(question, from_node_id=from_node_id, top_k=top_k)
    new_id = graph.promote_smart_ask(parent_id=from_node_id)

    if graph._last_smart_ask:
        for cited in graph._last_smart_ask.get("citations", []):
            graph.add_citation(new_id, cited)

    return new_id, answer


def improve_doc(graph, node_id, dry_run_embedding=False):
    if node_id not in graph.data:
        raise ValueError("Node ID not found")
    original = graph.data[node_id]
    improved_content = f"[IMPROVED VERSION]\n{original['response'][:300]}..."
    new_id = graph._generate_id()
    graph.data[new_id] = {
        "id": new_id,
        "type": "doc",
        "filename": f"{original.get('filename', 'improved')}",
        "parent_id": node_id,
        "prompt": f"Improved version of {original.get('filename', '')}",
        "response": improved_content,
        "children": [],
        "tags": ["doc", "improved"]
    }
    graph.data[node_id]["children"].append(new_id)

    graph.add_citation(new_id, node_id)

    config = load_config()
    if config.get("auto_embed", False):
        graph.embed_node(new_id, dry_run=dry_run_embedding)

    graph._save()
    return new_id


def simsearch(graph, query_text, top_k=3):
    query_vector = graph.get_embedding(query_text)
    dim = len(query_vector)

    # Build FAISS index
    index = faiss.IndexFlatL2(dim)
    id_map = []
    vectors = []

    for node_id, node in graph.data.items():
        id_map.append(node_id)
        vectors.append(np.array(node["embedding"], dtype=np.float32))

    if not vectors:
        print("No embedded nodes found.")
        return []

    index.add(np.stack(vectors))
    D, I = index.search(np.array([query_vector], dtype=np.float32), top_k)

    result_ids_scores = [
        (id_map[i], -D[0][j])  # negate distance to turn it into similarity
        for j, i in enumerate(I[0])
        if i < len(id_map)
    ]
    return result_ids_scores

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

def websearch(query: str, max_results=5):
    """
    Return a list of mock search results in Tavily-style format.
    Each result includes title, snippet, and URL.
    """
    return [
        {
            "title": f"Result {i + 1} for '{query}'",
            "snippet": f"This is a mock snippet for result {i + 1}.",
            "url": f"https://example.com/{i + 1}"
        }
        for i in range(max_results)
    ]

def save_web_result(graph, result, current_id=None, dry_run_embedding=False):
    node_id = graph._generate_id()
    graph.data[node_id] = {
        "id": node_id,
        "type": "web-result",
        "parent_id": current_id,
        "prompt": result["title"],
        "response": result["snippet"],
        "url": result["url"],
        "source": result.get("source", "tavily"),
        "children": [],
        "tags": ["web"],
    }
    if current_id and current_id in graph.data:
        graph.data[current_id]["children"].append(node_id)
    config = load_config()
    if config.get("auto_embed", False):
        graph.embed_node(node_id, dry_run=dry_run_embedding)
    graph._save()
    return node_id