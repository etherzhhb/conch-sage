import pytest
from chatcli.shell import ChatCLIShell

@pytest.fixture
def shell():
    sh = ChatCLIShell()
    sh.graph.storage_path = ":memory:"
    return sh

def test_new_reply_view(shell, capsys):
    shell.dispatch("new What is Halide?")
    shell.dispatch("reply It is a scheduling DSL.")
    shell.dispatch("view")
    out = capsys.readouterr().out
    assert "What is Halide" in out or "It is a scheduling DSL." in out

def test_embed_node_and_simsearch(shell, capsys):
    shell.dispatch("new Explain loop fusion.")
    shell.dispatch("embed-node")
    shell.dispatch("simsearch fusion")
    out = capsys.readouterr().out
    assert "fusion" in out.lower()

def test_smart_ask_and_promote(shell, capsys):
    shell.dispatch("new Tell me about vectorization.")
    shell.graph.data[shell.current_id]["response"] = "Vectorization speeds up code."
    shell.dispatch("smart-ask What is vectorization?")
    shell.dispatch("promote-smart-ask")
    out = capsys.readouterr().out
    assert "Promoted to new node" in out

def test_invalid_command(shell, capsys):
    shell.dispatch("foobar invalid command")
    out = capsys.readouterr().out
    assert "Unknown command" in out