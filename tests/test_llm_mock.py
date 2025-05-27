import pytest

def test_ask_llm_direct(graph):
    result = graph.ask_llm_direct("What is loop fusion?")
    assert "[TEST-MOCK]" in result


def test_ask_llm_with_context(graph):
    # Add a node with a citation
    root_id = graph.new("What is a compiler?")
    cited_id = graph.reply(root_id, "A program that translates code.")

    # Set citation edge manually
    graph.add_citation(root_id, cited_id)

    result = graph.ask_llm_with_context(root_id, "Explain the compiler stages.")
    assert "[TEST-MOCK]" in result
