import pytest
import yaml
from unittest.mock import patch

# Autouse fixture to patch load_config() across all tests
def load_test_config():
    with open("config.test.yaml") as f:
        return yaml.safe_load(f)

def pytest_sessionstart(session):
    patcher = patch("chatcli.core.config.load_config", side_effect=load_test_config)
    patcher.start()
    session._conch_config_patcher = patcher

def pytest_sessionfinish(session, exitstatus):
    if hasattr(session, "_conch_config_patcher"):
        session._conch_config_patcher.stop()


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


# Core graph fixture
@pytest.fixture
def graph():
    from chatcli.core.graph import ConversationGraph
    return ConversationGraph(storage_path=":memory:")
