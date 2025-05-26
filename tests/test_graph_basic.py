import pytest
from chatcli.core.graph import ConversationGraph

@pytest.fixture
def graph():
    return ConversationGraph(storage_path=":memory:")

def test_new_node(graph):
    nid = graph.new("What is Halide?")
    assert nid in graph.data
    assert graph.data[nid]["prompt"] == "What is Halide?"

def test_reply_node(graph):
    root = graph.new("Tell me about scheduling.")
    child = graph.reply(root, "Explain it")
    assert child in graph.data
    assert graph.data[child]["parent_id"] == root
    assert child in graph.data[root]["children"]

def test_get_embedding_mock(graph):
    emb = graph.get_embedding("loop fusion")
    assert isinstance(emb, list)
    assert len(emb) == 4

def test_embed_node(graph):
    nid = graph.new("What is scheduling?")
    graph.embed_node(nid)
    assert "embedding" in graph.data[nid]
    assert isinstance(graph.data[nid]["embedding"], list)

def test_simsearch(graph):
    a = graph.new("How Halide works?")
    b = graph.new("Tell me about TVM.")
    graph.embed_node(a)
    graph.embed_node(b)
    results = graph.simsearch("Halide", top_k=2)
    assert len(results) <= 2
    assert all(r in graph.data and 0 <= -score for r, score  in results)
