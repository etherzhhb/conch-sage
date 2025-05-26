import pytest
from chatcli.core.graph import ConversationGraph
from chatcli.core.graph_ops import websearch


def test_websearch_returns_expected_format():
    from chatcli.core.graph_ops import websearch
    results = websearch("What is Halide", max_results=3)
    assert isinstance(results, list)
    assert len(results) == 3
    for r in results:
        assert "title" in r
        assert "url" in r
        assert "snippet" in r

def test_saveurl_and_citeurl(graph, mock_websearch):
    nid = graph.new("Start")
    results = websearch("Halide scheduling")  # uses mocked version via monkeypatch
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


def test_diff_docs_between_nodes(graph, tmp_path):
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

def test_diff_docs_with_versioning(tmp_path):
    graph = ConversationGraph(storage_path=":memory:")

    # Create and save initial version
    nid = graph.new("Doc V1")
    graph.data[nid]["response"] = "Version 1 of the doc"
    file1 = tmp_path / "v1.md"
    graph.save_doc(nid, file1)
    graph.save_doc_version(nid, tmp_path)

    # Modify and save second version
    graph.data[nid]["response"] = "Version 2 of the doc with changes"
    file2 = tmp_path / "v2.md"
    graph.save_doc(nid, file2)
    graph.save_doc_version(nid, tmp_path)

    # Run diff
    diff_output = graph.diff_doc_versions(nid, tmp_path)
    assert isinstance(diff_output, str)
    assert "-Version 1 of the doc" in diff_output
    assert "+Version 2 of the doc with changes" in diff_output

