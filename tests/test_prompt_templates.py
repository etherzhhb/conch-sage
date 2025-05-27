import pytest

def test_suggest_tags_template(graph, monkeypatch):
    node_id = graph.new("Tag me")
    graph.data[node_id]["response"] = "This node needs good tags."

    captured = {}

    def mock_ask_llm_with_context(nid, prompt):
        captured["prompt"] = prompt
        return "[TAGS] example, mock, test"

    monkeypatch.setattr(graph, "ask_llm_with_context", mock_ask_llm_with_context)

    result = graph.suggest_tags(node_id, top_k=3)

    assert "[TAGS]" in result
    assert "organizing the following content" in captured["prompt"]


def test_suggest_replies_template(graph, monkeypatch):
    node_id = graph.new("Suggest reply")
    graph.data[node_id]["response"] = "Here's a conversational point."

    captured = {}

    def mock_ask_llm_with_context(nid, prompt):
        captured["prompt"] = prompt
        return "What about another example?"

    monkeypatch.setattr(graph, "ask_llm_with_context", mock_ask_llm_with_context)

    result = graph.suggest_replies(node_id, top_k=2)

    assert "example" in result.lower()
    assert "relevant follow-up questions" in captured["prompt"]


def test_suggest_validation_sources_template(graph, monkeypatch):
    node_id = graph.new("Validate this")
    graph.data[node_id]["response"] = "This is an unverifiable claim."

    captured = {}

    def mock_ask_llm_with_context(nid, prompt):
        captured["prompt"] = prompt
        return "Try searching on scholar.google.com."

    monkeypatch.setattr(graph, "ask_llm_with_context", mock_ask_llm_with_context)

    result = graph.suggest_validation_sources(node_id, top_k=2)

    assert "google" in result.lower()
    assert "validate or fact-check" in captured["prompt"]


def test_smart_ask_template(graph, monkeypatch):
    node_id = graph.new("Reference point")
    graph.data[node_id]["response"] = "Embedded facts go here."
    graph.embed_node(node_id)

    def mock_simsearch(query, top_k):
        return [(node_id, 0.01)]

    def mock_ask_with_context(nid, prompt):
        assert "QUESTION" in prompt
        return "This is a synthesized answer."

    graph.simsearch = mock_simsearch
    graph.ask_llm_with_context = mock_ask_with_context

    result = graph.smart_ask("What does this mean?", from_node_id=node_id)

    assert "synthesized" in result.lower()
