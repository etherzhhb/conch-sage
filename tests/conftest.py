import pytest

from chatcli.core.graph import ConversationGraph


# Mock the websearch function used by smart_ask() and suggest_tags()
@pytest.fixture
def mock_websearch(monkeypatch):
    def mock_websearch_fn(query: str, max_results=5):
        """
        Return a list of mock search results in Tavily-style format.
        Each result includes title, snippet, and URL.
        """
        return [
            {
                "title": f"Result {i + 1} for '{query}'",
                "snippet": f"This is a mock snippet for result {i + 1}.",
                "url": f"https://example.com/{i + 1}"
            }
            for i in range(max_results)
        ]

    monkeypatch.setattr(
        "chatcli.core.graph_ops.websearch",  mock_websearch_fn
    )

# Mock the LLM completion call for smart_ask(), improve_doc(), etc.
@pytest.fixture
def mock_llm(monkeypatch):
    def mock_llm_fn(*args, **kwargs):
        prompt = args[-1] if args else kwargs.get("prompt", "")
        return f"[MOCK LLM RESPONSE]\nPrompt: {prompt}"

    monkeypatch.setattr(
        "chatcli.core.graph_llm.ask_llm_with_context",
        mock_llm_fn
    )

# Mock get_embedding to return predictable vectors
@pytest.fixture
def mock_embedding(monkeypatch):
    monkeypatch.setattr(
        "chatcli.core.graph_ops.get_embedding",
        lambda text: [0.1] * 768  # Simulate OpenAI-style embedding
    )

@pytest.fixture
def graph():
    return ConversationGraph(storage_path=":memory:")
