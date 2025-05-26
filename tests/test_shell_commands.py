import pytest
from chatcli.shell import ChatCLIShell

@pytest.fixture
def shell():
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

def test_invalid_command(shell, capsys):
    shell.onecmd("foobar invalid command")
    err = capsys.readouterr().err
    assert "Unknown syntax: foobar invalid command" in err