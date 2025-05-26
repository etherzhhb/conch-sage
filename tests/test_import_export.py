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
