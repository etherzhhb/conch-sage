import pytest
from chatcli.core.graph import ConversationGraph

@pytest.fixture
def graph():
    return ConversationGraph(storage_path=":memory:")

def test_mock_websearch(graph):
    results = graph.mock_websearch("what is Halide", max_results=3)
    assert isinstance(results, list)
    assert len(results) == 3
    for r in results:
        assert "title" in r and "url" in r

def test_saveurl_and_citeurl(graph):
    nid = graph.new("Start")
    results = graph.mock_websearch("Halide scheduling")
    url_node = graph.save_web_result(results[0], current_id=nid)
    graph.add_citation(nid, url_node)
    assert url_node in graph.data
    assert "url" in graph.data[url_node]
    assert url_node in graph.data[nid]["citations"]

def test_import_doc(graph, tmp_path):
    sample_path = tmp_path / "test.md"
    sample_path.write_text("# Hello\nThis is a test document.")
    nid = graph.import_doc(str(sample_path))
    assert nid in graph.data
    assert "Hello" in graph.data[nid]["response"]

def test_diff_docs(graph, tmp_path):
    a = graph.new("Design v1")
    graph.data[a]["response"] = "We use a single thread."
    b = graph.reply(a, "Revise it")
    graph.data[b]["response"] = "We use multiple threads."

    path_a = tmp_path / "design_v1.md"
    path_b = tmp_path / "design_v2.md"
    graph.save_doc(a, path_a)
    graph.save_doc(b, path_b)

    diff = graph.diff_docs(a, b)
    assert "---" in diff and "+++" in diff
    assert "multiple threads" in diff

def test_import_and_improve_doc(tmp_path):
    graph = ConversationGraph(storage_path=":memory:")

    # Simulate document to import
    doc_path = tmp_path / "doc1.md"
    doc_path.write_text("This is a document about pipelining.")

    node_id = graph.import_doc(str(doc_path))
    assert node_id in graph.data
    assert "imported document" in graph.data[node_id]["prompt"].lower()
    assert "pipelining" in graph.data[node_id]["response"].lower()

    # Improve the imported doc
    improved_id = graph.improve_doc(node_id)
    assert improved_id in graph.data
    assert improved_id in graph.data[node_id]["children"]

    improved_node = graph.data[improved_id]
    assert "prompt" in improved_node and "improved" in improved_node["prompt"].lower()
    assert "response" in improved_node and len(improved_node["response"]) > 0
