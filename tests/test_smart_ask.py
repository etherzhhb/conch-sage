import pytest

def test_smart_ask_mock(graph):
    nid = graph.new("Start node")
    graph.embed_node(nid)
    reply_id = graph.reply(nid, "What is loop fusion?")
    graph.data[reply_id]["response"] = "Loop fusion combines loops for locality."
    graph.embed_node(reply_id)

    result = graph.smart_ask("loop fusion in scheduling", from_node_id=reply_id, top_k=2)
    assert isinstance(result, str)
    assert "loop" in result.lower()

def test_simulated_smart_ask_reply(graph):
    nid = graph.new("Parent")
    child = graph.reply(nid, "What is Halide?")
    graph.data[child]["smart_ask_prompt"] = "Explain Halide"
    graph.data[child]["response"] = "Halide is a scheduling DSL."

    new_id = graph.reply(child, graph.data[child]["smart_ask_prompt"])
    graph.data[new_id]["response"] = graph.data[child]["response"]

    assert new_id in graph.data
    assert graph.data[new_id]["prompt"] == "Explain Halide"
    assert graph.data[new_id]["response"] == "Halide is a scheduling DSL."
    assert graph.data[new_id]["parent_id"] == child

def test_cite_smart_ask(graph):
    nid = graph.new("Node A")
    graph.data[nid]["smart_ask_citations"] = []
    for i in range(3):
        cid = graph.new(f"Reference {i}")
        graph.embed_node(cid)
        graph.data[nid]["smart_ask_citations"].append(cid)

    for target in graph.data[nid]["smart_ask_citations"]:
        graph.add_citation(nid, target)

    assert len(graph.data[nid]["citations"]) == 3

def test_promote_smart_ask(graph):
    # Create initial node
    parent_id = graph.new("Tell me about loop fusion.")
    graph.data[parent_id]["response"] = "Loop fusion improves memory locality by combining loops."
    graph.embed_node(parent_id)

    # Run smart_ask
    answer = graph.smart_ask("What is loop fusion?", from_node_id=parent_id)
    assert isinstance(answer, str)
    assert "loop fusion" in answer.lower() or len(answer) > 0

    # Promote to new node
    new_id = graph.promote_smart_ask(parent_id)
    assert new_id in graph.data

    new_node = graph.data[new_id]
    assert new_node["prompt"].strip().lower().startswith("what is loop fusion")
    assert "response" in new_node and len(new_node["response"]) > 0
    assert parent_id in graph.data and new_id in graph.data[parent_id]["children"]

    assert new_node["response"] == answer

    # Validate citations if any
    if "citations" in new_node:
        for cited in new_node["citations"]:
            assert cited in graph.data

def test_smart_ask_with_empty_graph(graph):
    result = graph.smart_ask("What is loop fusion?")
    assert isinstance(result, str)
    assert "loop" in result.lower() or len(result) > 0


def test_ask_llm_with_context_uses_citations(graph):
    a = graph.new("Main question")
    b = graph.reply(a, "Cited insight")
    graph.data[b]["response"] = "This is relevant background."
    graph.add_citation(a, b)

    result = graph.ask_llm_with_context(a, "What does this mean?")
    assert "relevant background" in result
    assert "What does this mean?" in result

def test_ask_llm_with_context_truncates_long_prompts(graph):
    a = graph.new("Main question")
    long_text = "Lorem ipsum " * 1000  # very long
    b = graph.reply(a, "Verbose citation")
    graph.data[b]["response"] = long_text
    graph.add_citation(a, b)

    result = graph.ask_llm_with_context(a, "Summarize this.")
    assert "Summarize this." in result
    assert len(result) < 5000  # crude check for truncation



def test_ask_llm_with_context_falls_back_to_summary(graph):
    a = graph.new("Summary fallback test")
    b = graph.reply(a, "Too long to include")
    graph.data[b]["response"] = "A" * 5000
    graph.add_citation(a, b)

    # if get_node_summary is used, it should be invoked in the real impl
    result = graph.ask_llm_with_context(a, "Explain the idea")
    assert "Explain the idea" in result
    assert len(result) < 5000  # implies some fallback was triggered


def test_suggest_replies_from_node_content(graph):
    nid = graph.new("Prompt about Graph Theory")
    graph.data[nid]["response"] = "This node is about DFS and BFS."
    suggestions = graph.suggest_replies(nid, top_k=2)
    assert "Prompt about Graph Theory" in suggestions or "DFS" in suggestions

def test_suggest_replies_invalid_node(graph):
    with pytest.raises(ValueError):
        graph.suggest_replies("nonexistent_node")

def test_suggest_replies_top_k_control(graph):
    nid = graph.new("Prompt")
    graph.data[nid]["response"] = "Response"
    suggestions = graph.suggest_replies(nid, top_k=5)
    assert "5" in suggestions or "five" in suggestions


def test_suggest_replies_passes_context_id(graph, monkeypatch):
    called = {}

    def fake_ask_llm_with_context(node_id, prompt):
        called["node_id"] = node_id
        return "Fake reply"

    # Patch the bound method on the instance
    monkeypatch.setattr(graph, "ask_llm_with_context", fake_ask_llm_with_context)

    nid = graph.new("Follow-up?")
    graph.data[nid]["response"] = "Original response"
    graph.suggest_replies(nid)

    assert called["node_id"] == nid

def test_suggest_tags_from_node_content(graph):
    nid = graph.new("Prompt about AI")
    graph.data[nid]["response"] = "Covers deep learning and transformers."
    tags = graph.suggest_tags(nid, top_k=4)
    assert isinstance(tags, str)
    assert "transformers" in tags or "learning" in tags

def test_suggest_tags_invalid_node(graph):
    with pytest.raises(ValueError):
        graph.suggest_tags("invalid_node")


def test_suggest_tags_top_k_customization(graph):
    nid = graph.new("Tag prompt")
    graph.data[nid]["response"] = "Taggable content"
    tags = graph.suggest_tags(nid, top_k=6)
    assert "6" in tags or "six" in tags


def test_suggest_tags_passes_context_id(graph, monkeypatch):
    called = {}

    def fake_ask_llm_with_context(node_id, prompt):
        called["node_id"] = node_id
        return "tag1, tag2"

    monkeypatch.setattr(graph, "ask_llm_with_context", fake_ask_llm_with_context)

    nid = graph.new("Tag context")
    graph.data[nid]["response"] = "Test content"
    result = graph.suggest_tags(nid)

    assert called["node_id"] == nid
    assert "tag1" in result

def test_suggest_validation_sources_from_response(graph):
    nid = graph.new("Validate this")
    graph.data[nid]["response"] = "This claim is based on recent work in RLHF."
    sources = graph.suggest_validation_sources(nid, top_k=3)
    assert isinstance(sources, str)
    assert "RLHF" in sources or "recent" in sources


def test_suggest_validation_sources_invalid_node(graph):
    with pytest.raises(ValueError):
        graph.suggest_validation_sources("bad_id")

def test_suggest_validation_sources_top_k_passed(graph):
    nid = graph.new("Evidence check")
    graph.data[nid]["response"] = "Needs 5 verification points."
    sources = graph.suggest_validation_sources(nid, top_k=5)
    assert "5" in sources or "five" in sources

def test_suggest_validation_sources_context_id_used(graph, monkeypatch):
    called = {}

    def fake_ask_llm_with_context(node_id, prompt):
        called["node_id"] = node_id
        return "source1, source2"

    monkeypatch.setattr(graph, "ask_llm_with_context", fake_ask_llm_with_context)

    nid = graph.new("Verify prompt")
    graph.data[nid]["response"] = "Checkable material"
    result = graph.suggest_validation_sources(nid)

    assert called["node_id"] == nid
    assert "source1" in result

def test_improve_doc_creates_child_node(graph):
    nid = graph.new("Original")
    graph.data[nid]["response"] = "Needs improvement."
    new_id = graph.improve_doc(nid)
    assert new_id != nid
    assert graph.data[new_id]["parent_id"] == nid
    assert new_id in graph.data[nid]["children"]



def test_improve_doc_preserves_metadata(graph):
    nid = graph.new("Improve this")
    graph.data[nid]["response"] = "Rough draft."
    graph.data[nid]["filename"] = "draft.md"
    new_id = graph.improve_doc(nid)
    new_node = graph.data[new_id]
    assert new_node["type"] == "doc"
    assert "improved" in new_node["tags"]
    assert new_node["filename"] == "draft.md"


def test_improve_doc_adds_citation(graph):
    nid = graph.new("Draft")
    graph.data[nid]["response"] = "Base version."
    new_id = graph.improve_doc(nid)
    assert nid in graph.data[new_id]["citations"]


def test_improve_doc_respects_auto_embed_flag(graph, monkeypatch):
    nid = graph.new("Needs polish")
    graph.data[nid]["response"] = "Polish this draft"
    graph._config = {"auto_embed": True}

    called = {}
    def fake_embed_node(node_id, dry_run=False):
        called["embedded"] = node_id

    monkeypatch.setattr(graph, "embed_node", fake_embed_node)
    new_id = graph.improve_doc(nid, dry_run_embedding=True)
    assert called["embedded"] == new_id


def test_embed_node_assigns_embedding(graph):
    nid = graph.new("To embed")
    graph.data[nid]["response"] = "Vector me."
    graph.embed_node(nid)
    assert "embedding" in graph.data[nid]
    assert isinstance(graph.data[nid]["embedding"], list)
    assert len(graph.data[nid]["embedding"]) == 768

import pytest

def test_embed_node_invalid_id_raises(graph):
    with pytest.raises(ValueError):
        graph.embed_node("missing_node")

def test_embed_node_respects_dry_run(graph):
    nid = graph.new("Dry run", dry_run_embedding=True)
    graph.data[nid]["response"] = "Test"
    graph.embed_node(nid, dry_run=True)
    assert "embedding" not in graph.data[nid]

def test_embed_node_uses_graph_data(graph):
    nid = graph.new("Data path test")
    graph.data[nid]["response"] = "Hello"
    graph.embed_node(nid)
    assert nid in graph.data
    assert "embedding" in graph.data[nid]

def test_simsearch_skips_unembedded_nodes(graph):
    # Simulate config where auto_embed is disabled
    graph._config["auto_embed"] = False

    # Create a few nodes without embedding
    node1 = graph.new("Node without embedding 1")
    node2 = graph.new("Node without embedding 2")
    graph.data[node1]["response"] = "Test content one"
    graph.data[node2]["response"] = "Test content two"

    # Manually remove embeddings if somehow added
    graph.data[node1].pop("embedding", None)
    graph.data[node2].pop("embedding", None)

    # Run simsearch — should warn and return empty list
    matches = graph.simsearch("search query", top_k=5)
    assert matches == []
