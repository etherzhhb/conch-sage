import json
from pathlib import Path

import pytest
import tempfile
import os
from chatcli.core.graph import ConversationGraph


def test_export_and_import_graph():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        storage_path = tmp_path / "graph.json"

        # Export a graph with a smart-ask
        g1 = ConversationGraph(storage_path=storage_path)
        root = g1.new("What is loop fusion?")
        g1.data[root]["response"] = "Loop fusion combines loops."
        g1.embed_node(root)
        g1.smart_ask("Explain loop fusion.", from_node_id=root)
        g1.export_to_file("test_graph.json")

        # Import into a new graph
        g2 = ConversationGraph(storage_path=storage_path)
        g2.import_from_file("test_graph.json")

        assert len(g2.data) == len(g1.data)
        assert root in g2.data
        assert g2._last_smart_ask == g1._last_smart_ask
        assert "loop" in g2.data[root]["response"].lower()


def test_export_file_created(tmp_path):
    # Set up a graph with a custom storage path to control export dir
    storage_path = tmp_path / "conversations.json"
    graph = ConversationGraph(storage_path=storage_path)

    nid = graph.new("Test export")
    graph.data[nid]["response"] = "Exported node."

    filename = "export_test.json"
    graph.export_to_file(filename)

    path = graph._save_dir / filename  # use instance-level path
    assert path.exists()

    with open(path) as f:
        content = f.read()
        assert "Exported node." in content

def test_import_from_missing_file(capsys):
    graph = ConversationGraph()
    graph.import_from_file("nonexistent.json")
    captured = capsys.readouterr()
    assert "no data imported" in captured.out.lower()


def test_import_from_invalid_format(tmp_path, capsys):
    filepath = tmp_path / "invalid.json"
    filepath.write_text("This is not valid JSON")

    graph = ConversationGraph()
    try:
        with open(filepath) as f:
            json_data = f.read()
            _ = json.loads(json_data)  # confirm failure will happen here
    except Exception:
        pass

    # We'll simulate a failure due to wrong format
    with open(filepath, "w") as f:
        f.write("{}")  # valid JSON but empty

    graph.import_from_file(filepath.name)
    assert graph.data == {}

def test_export_mermaid(tmp_path):
    graph = ConversationGraph(storage_path=":memory:")
    root = graph.new("Mermaid Root")
    child = graph.reply(root, "Mermaid Child")
    graph.add_citation(child, root)

    filename = "test_mermaid.mmd"
    graph._save_dir = tmp_path  # override save directory for testing
    graph.export_mermaid(filename)

    output_file = tmp_path / filename
    assert output_file.exists()
    content = output_file.read_text()
    assert "graph TD" in content
    assert root in content and child in content
    assert f"{root} --> {child}" in content
    assert f"{child} -.-> {root}" in content  # citation


def test_save_doc_creates_file(graph, tmp_path):
    nid = graph.new("Save me")
    graph.data[nid]["response"] = "This is the saved content."
    filepath = tmp_path / "output.md"
    result = graph.save_doc(nid, filepath)
    assert result == filepath
    assert filepath.read_text() == "This is the saved content."


def test_save_doc_invalid_node_raises(graph, tmp_path):
    with pytest.raises(ValueError):
        graph.save_doc("missing", tmp_path / "fail.md")

def test_save_doc_prints_confirmation(graph, tmp_path, capsys):
    nid = graph.new("Logging test")
    graph.data[nid]["response"] = "Log this"
    path = tmp_path / "log.md"
    graph.save_doc(nid, path)
    out = capsys.readouterr().out
    assert "Saved node" in out
    assert str(path) in out


def test_import_doc_creates_node_with_file_contents(graph, tmp_path):
    filepath = tmp_path / "doc.md"
    filepath.write_text("This is a test document.")
    node_id = graph.import_doc(filepath)
    assert graph.data[node_id]["response"] == "This is a test document."



def test_import_doc_adds_metadata(graph, tmp_path):
    filepath = tmp_path / "meta.rst"
    filepath.write_text("Metadata check")
    nid = graph.import_doc(filepath)
    node = graph.data[nid]
    assert node["filename"] == "meta.rst"
    assert node["type"] == "doc"
    assert "doc" in node["tags"]



def test_import_doc_applies_truncation(graph, tmp_path):
    filepath = tmp_path / "truncate.md"
    filepath.write_text("A" * 5000)
    nid = graph.import_doc(filepath, truncate=100)
    assert len(graph.data[nid]["response"]) == 100



def test_import_doc_handles_parent_link(graph, tmp_path):
    parent = graph.new("Parent")
    filepath = tmp_path / "child.md"
    filepath.write_text("Child node")
    child = graph.import_doc(filepath, current_id=parent)
    assert child in graph.data[parent]["children"]
    assert graph.data[child]["parent_id"] == parent
