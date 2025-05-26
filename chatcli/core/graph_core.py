# chatcli/core/graph_core.py

import json, os
import uuid
from pathlib import Path
from chatcli.core.config import load_config
from chatcli.core.graph_io import save_to_file


class GraphCore:
    def __init__(self, storage_path=None):
        self._in_memory = storage_path == ":memory:"
        self._data = {}
        if self._in_memory:
            self._storage_path = None
            self._save_dir = Path("data")
        else:
            self._storage_path = Path(storage_path or "data/conversations.json")
            self._save_dir = self._storage_path.parent

    @property
    def data(self):
        return self._data

    def get(self, node_id):
        return self.data.get(node_id, None)

    def _generate_id(self):
        return uuid.uuid4().hex[:8]

    def add_node(self, prompt, parent_id=None):
        node_id = self._generate_id()
        node = {
            "id": node_id,
            "prompt": prompt,
            "response": "",
            "parent_id": parent_id,
            "children": [],
            "tags": [],
        }
        self._data[node_id] = node
        if parent_id and parent_id in self._data:
            self._data[parent_id]["children"].append(node_id)
        self._save()
        return node_id

    def get_node(self, node_id):
        return self._data.get(node_id)

    def get_children(self, node_id):
        return self._data.get(node_id, {}).get("children", [])

    def get_parents(self, node_id):
        return [n["id"] for n in self._data.values() if node_id in n.get("children", [])]

    def tag_node(self, node_id, tag):
        if node_id in self._data:
            self._data[node_id].setdefault("tags", []).append(tag)
            self._save()

    def list_saved_files(graph):
        return [f.name for f in graph._save_dir.glob("*.json")]

    def _save(self):
        self.save_to_file(self._storage_path)

    def save_to_file(self, filename):
        save_to_file(self, filename)

    def _has_path(self, start_id, target_id, visited=None):
        if visited is None:
            visited = set()
        if start_id == target_id:
            return True
        visited.add(start_id)
        for neighbor in self.data.get(start_id, {}).get("citations", []):
            if neighbor not in visited and self._has_path(neighbor, target_id, visited):
                return True
        return False

    def ancestors(self, node_id):
        path = []
        current = self.data.get(node_id)
        while current and current.get("parent_id"):
            parent_id = current["parent_id"]
            path.append(parent_id)
            current = self.data.get(parent_id)
        return path

    def descendants(self, node_id):
        result = []

        def dfs(nid):
            children = self.data.get(nid, {}).get("children", [])
            for child_id in children:
                result.append(child_id)
                dfs(child_id)

        dfs(node_id)
        return result

    def get_citations(self, node_id):
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        return self.data[node_id].get("citations", [])

    def get_cited_by(self, node_id):
        return [
            n["id"] for n in self.data.values()
            if node_id in n.get("citations", [])
        ]

    def filter_cites(self, node_id):
        return self.get_citations(node_id)

    def filter_cited_by(self, node_id):
        return self.get_cited_by(node_id)

    def filter_related(self, node_id):
        cited = set(self.get_citations(node_id))
        citing = set(self.get_cited_by(node_id))
        return list(cited.union(citing))

    def describe_nodes(self, node_ids):
        return [
            f"[{nid}] {self.data[nid]['prompt'][:60]}..." for nid in node_ids if nid in self.data
        ]

    def preview_node(self, node_id):
        if node_id not in self.data:
            return f"[{node_id}] (not found)"
        node = self.data[node_id]
        prompt = node['prompt'][:80].replace("\n", " ")
        return f"[{node_id}] {prompt}"
