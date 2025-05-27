import pytest
from unittest.mock import patch, MagicMock
from chatcli.shell import ChatCLIShell

@pytest.fixture
def shell():
    with patch("chatcli.shell.PromptSession") as MockSession:
        # Mock the PromptSession instance
        mock_session = MagicMock()
        MockSession.return_value = mock_session

        # Initialize ChatCLIShell with the mocked PromptSession
        sh = ChatCLIShell()
        sh.graph.storage_path = ":memory:"
        return sh

def test_new_reply_view(shell, capsys):
    shell.onecmd("new What is Halide?")
    shell.onecmd("reply It is a scheduling DSL.")
    shell.onecmd("view")
    out = capsys.readouterr().out
    assert "What is Halide" in out or "It is a scheduling DSL." in out

def test_embed_node_and_simsearch(shell, capsys):
    shell.onecmd("new Explain loop fusion.")
    shell.onecmd("embed_node")
    shell.onecmd("simsearch fusion")
    out = capsys.readouterr().out
    assert "fusion" in out.lower()

def test_smart_ask_and_promote(shell, capsys):
    shell.onecmd("new Tell me about vectorization.")
    shell.graph.data[shell.current_id]["response"] = "Vectorization speeds up code."
    shell.onecmd("smart_ask What is vectorization?")
    shell.onecmd("promote_smart_ask")
    out = capsys.readouterr().out
    assert "Promoted to new node" in out

def test_smart_ask_with_promote(shell, capsys):
    shell.onecmd("new What is vectorization?")
    shell.graph.data[shell.current_id]["response"] = "Vectorization improves data throughput."
    shell.onecmd("smart_ask What is SIMD? --promote")
    out = capsys.readouterr().out
    assert "Promoted to new node" in out

def test_invalid_command(shell, capsys):
    shell.onecmd("foobar invalid command")
    out = capsys.readouterr().out
    assert "Unknown syntax: foobar invalid command" in out

def test_suggest_replies(shell, capsys):
    shell.onecmd("new What is loop fusion?")
    shell.graph.data[shell.current_id]["response"] = "Loop fusion merges multiple loops to reduce overhead."
    shell.onecmd("suggest_replies")
    out = capsys.readouterr().out
    assert "Suggestions" in out

def test_suggest_tags(shell, capsys):
    shell.onecmd("new Explain async GPU compute.")
    shell.graph.data[shell.current_id]["response"] = "Async GPU compute overlaps data transfers and kernel execution."
    shell.onecmd("suggest_tags")
    out = capsys.readouterr().out
    assert "Tag Suggestions" in out

def test_suggest_validation_sources(shell, capsys):
    shell.onecmd("new Halide optimizes compute and schedule.")
    shell.graph.data[shell.current_id]["response"] = "Halide separates what to compute from how to compute it."
    shell.onecmd("suggest_validation_sources")
    out = capsys.readouterr().out
    assert "Validation Suggestions" in out

def test_smart_thread(shell, capsys):
    shell.onecmd("new What is loop fusion?")
    shell.graph.data[shell.current_id]["response"] = "Loop fusion improves locality."
    shell.onecmd("smart_thread How does it affect memory?")
    out = capsys.readouterr().out
    assert "Smart Thread Response" in out
    assert "New node" in out

def test_goto_valid_node(shell, capsys):
    shell.onecmd("new Root node")
    root_id = shell.current_id
    shell.onecmd("reply Child node")
    child_id = shell.current_id

    # Now go back to root
    shell.onecmd(f"goto {root_id}")
    assert shell.current_id == root_id

def test_goto_invalid_node(shell, capsys):
    shell.onecmd("new Some node")
    shell.onecmd("goto nonexistent123")
    out = capsys.readouterr().out
    assert "Node nonexistent123 not found." in out

def test_parent_from_child(shell, capsys):
    shell.onecmd("new Root node")
    root_id = shell.current_id
    shell.onecmd("reply Child node")
    child_id = shell.current_id

    # Move back to parent
    shell.onecmd("parent")
    out = capsys.readouterr().out

    assert shell.current_id == root_id
    assert f"Moved to parent node {root_id}" in out

def test_parent_from_root(shell, capsys):
    shell.onecmd("new Top-level node")
    root_id = shell.current_id

    shell.onecmd("parent")
    out = capsys.readouterr().out

    # Should print message and keep current ID unchanged
    assert "This node has no parent." in out
    assert shell.current_id == root_id

def test_print_tree_root(shell, capsys):
    shell.onecmd("new First root")
    shell.onecmd("new Second root")
    shell.onecmd("tree_all")
    out = capsys.readouterr().out

    assert "First root" in out
    assert "Second root" in out

def test_print_tree_parent_from_child(shell, capsys):
    shell.onecmd("new Parent node")
    parent_id = shell.current_id
    shell.onecmd("reply Child node")

    shell.onecmd("tree parent")
    out = capsys.readouterr().out

    assert "Parent node" in out
    assert "Child node" in out

def test_print_tree_parent_from_root(shell, capsys):
    shell.onecmd("new Root node")
    root_id = shell.current_id

    shell.onecmd("tree parent")
    out = capsys.readouterr().out

    assert "This node has no parent" in out
    assert "Root node" in out
