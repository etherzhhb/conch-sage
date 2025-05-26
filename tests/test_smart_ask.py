import pytest
from chatcli.core.graph import ConversationGraph

@pytest.fixture
def graph():
    return ConversationGraph(storage_path=":memory:")

def test_smart_ask_mock(graph):
    nid = graph.new("Start node")
    graph.embed_node(nid)
    reply_id = graph.reply(nid, "What is loop fusion?")
    graph.data[reply_id]["response"] = "Loop fusion combines loops for locality."
    graph.embed_node(reply_id)

    result = graph.smart_ask("loop fusion in scheduling", from_node_id=reply_id, top_k=2)
    assert isinstance(result, str)
    assert "loop" in result.lower()

def test_simulated_smart_ask_reply(graph):
    nid = graph.new("Parent")
    child = graph.reply(nid, "What is Halide?")
    graph.data[child]["smart_ask_prompt"] = "Explain Halide"
    graph.data[child]["response"] = "Halide is a scheduling DSL."

    new_id = graph.reply(child, graph.data[child]["smart_ask_prompt"])
    graph.data[new_id]["response"] = graph.data[child]["response"]

    assert new_id in graph.data
    assert graph.data[new_id]["prompt"] == "Explain Halide"
    assert graph.data[new_id]["response"] == "Halide is a scheduling DSL."
    assert graph.data[new_id]["parent_id"] == child

def test_cite_smart_ask(graph):
    nid = graph.new("Node A")
    graph.data[nid]["smart_ask_citations"] = []
    for i in range(3):
        cid = graph.new(f"Reference {i}")
        graph.embed_node(cid)
        graph.data[nid]["smart_ask_citations"].append(cid)

    for target in graph.data[nid]["smart_ask_citations"]:
        graph.add_citation(nid, target)

    assert len(graph.data[nid]["citations"]) == 3

def test_promote_smart_ask(graph):
    # Create initial node
    parent_id = graph.new("Tell me about loop fusion.")
    graph.data[parent_id]["response"] = "Loop fusion improves memory locality by combining loops."
    graph.embed_node(parent_id)

    # Run smart_ask
    answer = graph.smart_ask("What is loop fusion?", from_node_id=parent_id)
    assert isinstance(answer, str)
    assert "loop fusion" in answer.lower() or len(answer) > 0

    # Promote to new node
    new_id = graph.promote_smart_ask(parent_id)
    assert new_id in graph.data

    new_node = graph.data[new_id]
    assert new_node["prompt"].strip().lower().startswith("what is loop fusion")
    assert "response" in new_node and len(new_node["response"]) > 0
    assert parent_id in graph.data and new_id in graph.data[parent_id]["children"]

    # Validate citations if any
    if "citations" in new_node:
        for cited in new_node["citations"]:
            assert cited in graph.data