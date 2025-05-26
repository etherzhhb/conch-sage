
import pytest
import json
from chatcli.core.graph import ConversationGraph

@pytest.fixture
def graph():
    return ConversationGraph(storage_path=":memory:")

def test_save_and_load(tmp_path):
    path = tmp_path / "graph.json"
    g = ConversationGraph(storage_path=path)
    nid = g.new("Persistence test")
    g.data[nid]["response"] = "Persisted"
    g._save()

    g2 = ConversationGraph(storage_path=path)  # load happens in __init__
    assert nid in g2.data
    assert g2.data[nid]["response"] == "Persisted"

def test_citation_cycle_prevention(graph):
    a = graph.new("A")
    b = graph.reply(a, "B")
    graph.add_citation(a, b)
    # Placeholder: only test cycle if logic prevents it; otherwise document it
    with pytest.raises(Exception):
        graph.add_citation(b, a)

def test_ancestor_and_descendant(graph):
    root = graph.new("Root")
    child = graph.reply(root, "Child")
    grandchild = graph.reply(child, "Grandchild")
    assert root in graph.ancestors(grandchild)
    assert grandchild in graph.descendants(root)

def test_import_partial_graph(tmp_path):
    path = tmp_path / "partial.json"
    path.write_text('{"bad_json": true')  # malformed JSON

    g = ConversationGraph(storage_path=":memory:")  # don't load from broken file
    g.import_from_file(str(path))  # should fail gracefully
    assert g.data == {}
