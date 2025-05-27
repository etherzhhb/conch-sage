# chatcli/core/graph.py

from chatcli.core.config import load_config
from chatcli.core.embedding_provider import get_embedding_provider
from chatcli.core.graph_core import GraphCore
from chatcli.core.graph_io import (
    import_doc, save_doc, save_doc_version,
    load_from_file,
    diff_doc_versions, diff_docs, import_from_file, export_mermaid, load_graph_state, save_to_file,
)
from chatcli.core.graph_llm import (
    suggest_replies,
    suggest_tags,
    suggest_validation_sources, ask_llm_with_context, ask_llm_direct,
    estimate_tokens, get_embedding, embed_node
)
from chatcli.core.graph_ops import (
    smart_ask,
    promote_smart_ask,
    cite_smart_ask,
    smart_thread, improve_doc, simsearch, save_web_result
)


class ConversationGraph(GraphCore):
    def __init__(self, storage_path=":memory:"):
        super().__init__(storage_path)
        self._data, self._last_smart_ask = load_graph_state(self)
        self._config = load_config()
        self._embedding_provider = None

    def get_embedding_provider(self):
        if self._embedding_provider is None:
            self._embedding_provider = get_embedding_provider(self._config)
        return self._embedding_provider

    def update_last_smart_ask(self, from_node_id, query_text, answer, citations):
        self._last_smart_ask = {
            "from_node_id": from_node_id,
            "question": query_text.strip(),
            "response": answer,
            "citations": citations,
        }

    def new_thread(self, prompt, dry_run_embedding=False):
        node_id = self.add_node(prompt)
        self._data[node_id]["response"] = f"[MOCK RESPONSE to: {prompt}]"
        if self._config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()
        return node_id

    def new(self, *args, **kwargs):
        return self.new_thread(*args, **kwargs)

    def reply(self, parent_id, prompt, dry_run_embedding=False):
        if parent_id not in self._data:
            raise ValueError("Parent ID not found")

        node_id = self.add_node(prompt, parent_id=parent_id)
        self._data[node_id]["response"] = f"[MOCK RESPONSE to: {prompt}]"
        if self._config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()
        return node_id

    def edit_response(self, node_id, new_response, dry_run_embedding=False):
        if node_id not in self._data:
            raise ValueError("Node ID not found")
        self._data[node_id]["response"] = new_response
        if self._config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()

    def add_comment(self, node_id, comment, dry_run_embedding=False):
        if node_id not in self._data:
            raise ValueError("Node ID not found")
        self._data[node_id]["comment"] = comment
        if self._config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()

    def retry(self, node_id, new_prompt=None, dry_run_embedding=False):
        if node_id not in self._data:
            raise ValueError("Node ID not found")
        prompt = new_prompt if new_prompt else self._data[node_id]["prompt"]
        self._data[node_id]["response"] = f"[MOCK RETRY to: {prompt}]"
        if new_prompt:
            self._data[node_id]["prompt"] = new_prompt
        if self._config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()

    def embed_node(self, node_id, dry_run=False):
        return embed_node(self, node_id, dry_run=dry_run)

    def get_embedding(self, text):
        return get_embedding(self, text=text)

    # LLM Suggestions
    def ask_llm_with_context(self, *args, **kwargs):
        return ask_llm_with_context(self, *args, **kwargs)

    # LLM Suggestions
    def ask_llm_direct(self, *args, **kwargs):
        return ask_llm_direct(self, *args, **kwargs)

    def estimate_tokens(self, *args, **kwargs):
        return estimate_tokens(self, *args, **kwargs)

    def suggest_replies(self, *args, **kwargs):
        return suggest_replies(self, *args, **kwargs)

    def suggest_tags(self, *args, **kwargs):
        return suggest_tags(self, *args, **kwargs)

    def suggest_validation_sources(self, *args, **kwargs):
        return suggest_validation_sources(self, *args, **kwargs)

    # Smart Workflows
    def smart_ask(self, *args, **kwargs):
        return smart_ask(self, *args, **kwargs)

    def promote_smart_ask(self, *args, **kwargs):
        return promote_smart_ask(self, *args, **kwargs)

    def cite_smart_ask(self, target_node_id=None):
        return cite_smart_ask(self, target_node_id)

    def smart_thread(self, *args, **kwargs):
        return smart_thread(self, *args, **kwargs)

    # File I/O
    def import_doc(self, *args, **kwargs):
        return import_doc(self, *args, **kwargs)

    def save_doc(self, *args, **kwargs):
        return save_doc(self, *args, **kwargs)

    def save_doc_version(self, *args, **kwargs):
        return save_doc_version(self, *args, **kwargs)

    def diff_doc_versions(self, *args, **kwargs):
        return diff_doc_versions(self, *args, **kwargs)

    def diff_docs(self, *args, **kwargs):
        return diff_docs(self, *args, **kwargs)

    def improve_doc(self, *args, **kwargs):
        return improve_doc(self, *args, **kwargs)

    def export_to_file(self, *args, **kwargs):
        return save_to_file(self, *args, **kwargs)

    def simsearch(self, *args, **kwargs):
        return simsearch(self, *args, **kwargs)

    def load_from_file(self, *args, **kwargs):
        return load_from_file(self, *args, **kwargs)

    def add_citation(self, from_node_id, to_node_id, dry_run_embedding=False):
        """
        Add a citation edge from one node to another, indicating that `from_node_id`
        references or builds upon the content of `to_node_id`.

        This creates a directed edge in the citation graph: from → to.
        The method ensures that this operation does not introduce a cycle, preserving
        the directed acyclic graph (DAG) invariant of the citation structure.

        Args:
            from_node_id (str): The ID of the citing node.
            to_node_id (str): The ID of the node being cited.
            dry_run_embedding (bool): If True, skip actual embedding update.

        Raises:
            ValueError: If either node ID is invalid or the citation would introduce a cycle.
        """
        if from_node_id not in self.data or to_node_id not in self.data:
            raise ValueError("Invalid node ID(s)")

        if self._has_path(to_node_id, from_node_id):
            raise ValueError("Citation would introduce a cycle")

        self.data[from_node_id].setdefault("citations", [])
        if to_node_id not in self.data[from_node_id]["citations"]:
            self.data[from_node_id]["citations"].append(to_node_id)

        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(from_node_id, dry_run=dry_run_embedding)

        self._save()

    def import_from_file(self, *args, **kwargs):
        return import_from_file(self, *args, **kwargs)

    def export_mermaid(self, *args, **kwargs):
        return export_mermaid(self, *args, **kwargs)

    def save_web_result(self, *args, **kwargs):
        return save_web_result(self, *args, **kwargs)