import sys

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
