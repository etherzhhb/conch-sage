import os

from chatcli.core.config import load_config
import uuid
from pathlib import Path
import json
import numpy as np
import faiss

from chatcli.core.mock import mock_llm_response


class ConversationGraph:

    def __init__(self, storage_path=None):
        if storage_path and storage_path != ":memory:":
            path = Path(storage_path)
            self._path = path
            self._save_dir = path.parent
            self.data, self._last_smart_ask = self._load(self._path)
        else:
            self._path = None
            self._save_dir = Path("data")
            self.data = {}
            self._last_smart_ask = None

    def _write_to_file(self, path):
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as f:
            json.dump({
                "nodes": self.data,
                "last_smart_ask": self._last_smart_ask
            }, f, indent=2)

    def _load(self, path):
        if not path.exists():
            return {}, None
        try:
            with open(path, "r") as f:
                obj = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: failed to load {path}: {e}")
            return {}, None
        return obj.get("nodes", {}), obj.get("last_smart_ask", None)

    def _save(self):
        if self._path is None:
            return

        self._write_to_file(self._path)

    def export_to_file(self, filename):
        """
        Export the full conversation graph to a JSON file, including smart-ask context.

        Args:
            filename (str): Name of the file to save to (relative to export directory).
        """
        filepath = self._save_dir / filename
        self._write_to_file(filepath)
        print(f"Exported full graph to {filepath}")

    def import_from_file(self, filename, dry_run_embedding=False):
        """
        Import a full conversation graph (including smart-ask context) from a JSON file.

        Args:
            filename (str): File name relative to the export directory.
            dry_run_embedding (bool): If True, skip actual embedding.
        """
        filepath = self._save_dir / filename
        self.data, self._last_smart_ask = self._load(filepath)

        if not self.data:
            print(f"No data imported from {filepath}")
            return

        config = load_config()
        if config.get("auto_embed", False):
            for node_id in self.data:
                self.embed_node(node_id, dry_run=dry_run_embedding)

        self._save()
        print(f"Imported full graph from {filepath}")

    def _generate_id(self):
        return str(uuid.uuid4())[:8]

    def new_thread(self, prompt, dry_run_embedding=False):
        node_id = self._generate_id()
        self.data[node_id] = {
            "id": node_id,
            "parent_id": None,
            "prompt": prompt,
            "response": f"[MOCK RESPONSE to: {prompt}]",
            "children": [],
            "tags": []
        }
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()
        return node_id

    def new(self, prompt):
        """Alias for new_thread(), used by CLI and tests"""
        return self.new_thread(prompt)

    def reply(self, parent_id, prompt, dry_run_embedding=False):
        if parent_id not in self.data:
            raise ValueError("Parent ID not found")

        node_id = self._generate_id()
        self.data[node_id] = {
            "id": node_id,
            "parent_id": parent_id,
            "prompt": prompt,
            "response": f"[MOCK RESPONSE to: {prompt}]",
            "children": [],
            "tags": []
        }
        self.data[parent_id]["children"].append(node_id)
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()
        return node_id

    def get(self, node_id):
        return self.data.get(node_id, None)

    def print_tree(self, root_id, indent=0):
        node = self.data.get(root_id)
        if not node:
            print("Node not found.")
            return
        comment_str = f"  # {node['comment']}" if 'comment' in node else ""
        summary_str = f"\n{' ' * (indent + 2)}[summary] {node['summary']}" if 'summary' in node else ""
        tag_str = f"  [tags: {', '.join(node['tags'])}]" if node['tags'] else ""
        subtree_summary_str = f"\n{' ' * (indent + 2)}[subtree_summary] {node['subtree_summary']}" if 'subtree_summary' in node else ""
        citation_str = f"\n{' ' * (indent + 2)}[cites] {', '.join(node['citations'])}" if 'citations' in node else ""
        print(
            " " * indent + f"[{node['id']}] {node['prompt']}{comment_str}{tag_str}" + summary_str + subtree_summary_str + citation_str)
        for child_id in node["children"]:
            self.print_tree(child_id, indent + 2)

    def edit_response(self, node_id, new_response, dry_run_embedding=False):
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        self.data[node_id]["response"] = new_response
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()

    def add_comment(self, node_id, comment, dry_run_embedding=False):
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        self.data[node_id]["comment"] = comment
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()

    def retry(self, node_id, new_prompt=None, dry_run_embedding=False):
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        prompt = new_prompt if new_prompt else self.data[node_id]["prompt"]
        self.data[node_id]["response"] = f"[MOCK RETRY to: {prompt}]"
        if new_prompt:
            self.data[node_id]["prompt"] = new_prompt
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()

    def list_saved_files(self):
        """
        List all saved JSON files in the configured save directory.

        Returns:
            list of str: Filenames of saved conversation graphs.
        """
        return [f.name for f in self._save_dir.glob("*.json")]

    def add_tag(self, node_id, tag, dry_run_embedding=False):
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        if "tags" not in self.data[node_id]:
            self.data[node_id]["tags"] = []
        if tag not in self.data[node_id]["tags"]:
            self.data[node_id]["tags"].append(tag)
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()

    def remove_tag(self, node_id, tag, dry_run_embedding=False):
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        if "tags" in self.data[node_id] and tag in self.data[node_id]["tags"]:
            self.data[node_id]["tags"].remove(tag)
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()

    def list_tags(self, node_id):
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        return self.data[node_id].get("tags", [])

    def summarize_subtree(self, node_id, dry_run_embedding=False):
        if node_id not in self.data:
            raise ValueError("Node ID not found")

        def gather_subtree_text(nid):
            node = self.data[nid]
            texts = [f"{node['prompt']} -> {node['response']}"]
            for child_id in node.get("children", []):
                texts.extend(gather_subtree_text(child_id))
            return texts

        full_text = "\n".join(gather_subtree_text(node_id))
        summary = f"[SUMMARY of subtree rooted at {node_id}]\n" + full_text[:300] + "..."
        self.data[node_id]["subtree_summary"] = summary
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()
        return summary

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

    def export_mermaid(self, filename):
        lines = ["graph TD"]
        for node_id, node in self.data.items():
            label = node['prompt'].replace('"', "'").replace("\n", " ")[:50]
            lines.append(f'{node_id}["{label}"]')
        for node_id, node in self.data.items():
            for child_id in node.get("children", []):
                lines.append(f"{node_id} --> {child_id}")
            for cited_id in node.get("citations", []):
                lines.append(f"{node_id} -.-> {cited_id}")
        filepath = Path("data") / filename
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        print(f"Exported to Mermaid format: {filepath}")

    def search(self, query):
        query_lower = query.lower()
        results = []
        for node in self.data.values():
            if (query_lower in node["prompt"].lower()
                    or query_lower in node["response"].lower()
                    or query_lower in node.get("comment", "").lower()
                    or query_lower in " ".join(node.get("tags", [])).lower()):
                results.append(node["id"])
        return results

    def mock_websearch(self, query, max_results=5):
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

    def save_web_result(self, result, current_id=None, dry_run_embedding=False):
        node_id = self._generate_id()
        self.data[node_id] = {
            "id": node_id,
            "type": "web-result",
            "parent_id": current_id,
            "prompt": result["title"],
            "response": result["snippet"],
            "url": result["url"],
            "source": result.get("source", "tavily"),
            "children": [],
            "tags": ["web"],
        }
        if current_id and current_id in self.data:
            self.data[current_id]["children"].append(node_id)
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()
        return node_id

    def ask_llm_with_context(self, node_id, question):
        config = load_config()
        provider = config["provider"]
        model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
        print(f"[LLM] Using {provider}: {model}")
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        citations = self.get_citations(node_id)
        context_parts = []
        token_limit = 1000  # configurable later
        token_count = 0
        for cid in citations:
            cited = self.data.get(cid)
            if cited:
                snippet = cited.get("response", "")[:200]
                title = cited.get("prompt", "")[:50]
                entry = f"- {title}: {snippet}"
            entry_tokens = self.estimate_tokens(entry)
            if token_count + entry_tokens <= token_limit:
                context_parts.append(entry)
                token_count += entry_tokens
            else:
                summary = self.summarize_text(snippet)
                self.data[cid]['summary'] = summary  # Save summary to node
                context_parts.append(f"- {title}: {summary}")
                break
        context = "\n".join(context_parts) if context_parts else "No supporting information available."
        response = f"[MOCK LLM RESPONSE]\nUsing sources:\n{context}\n\nAnswer: {question} is a good question!"
        return response

    def estimate_tokens(self, text):
        # Basic token estimate: ~1 token per 4 characters (OpenAI rough rule)
        return len(text) // 4

    def summarize_text(self, text, max_length=200):
        config = load_config()
        provider = config["provider"]
        model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
        print(f"[SUMMARIZER] Using {provider}: {model}")
        return "[SUMMARY] " + text[:max_length] + "..."

    def import_doc(self, filepath, current_id=None, dry_run_embedding=False):
        from pathlib import Path
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        content = path.read_text()
        node_id = self._generate_id()
        self.data[node_id] = {
            "id": node_id,
            "type": "doc",
            "filename": str(path.name),
            "parent_id": current_id,
            "prompt": f"Imported document: {path.name}",
            "response": content,
            "children": [],
            "tags": ["doc"]
        }
        if current_id:
            self.data[current_id]["children"].append(node_id)
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()
        return node_id

    def improve_doc(self, node_id, dry_run_embedding=False):
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        original = self.data[node_id]
        improved_content = f"[IMPROVED VERSION]\n{original['response'][:300]}..."
        new_id = self._generate_id()
        self.data[new_id] = {
            "id": new_id,
            "type": "doc",
            "filename": f"{original.get('filename', 'improved')}",
            "parent_id": node_id,
            "prompt": f"Improved version of {original.get('filename', '')}",
            "response": improved_content,
            "children": [],
            "tags": ["doc", "improved"]
        }
        self.data[node_id]["children"].append(new_id)
        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id, dry_run=dry_run_embedding)
        self._save()
        return new_id

    def save_doc(self, node_id, output_path):
        from pathlib import Path
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        content = self.data[node_id]["response"]
        Path(output_path).write_text(content)
        return output_path

    def save_doc_version(self, node_id, folder="docs"):
        import subprocess
        from pathlib import Path
        if node_id not in self.data:
            raise ValueError("Node ID not found")
        node = self.data[node_id]
        filename = f"{node_id}_{node.get('filename', 'doc.md')}"
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        filepath = path / filename
        filepath.write_text(node["response"])

        subprocess.run(["git", "add", str(filepath)], check=True)
        commit_msg = f"Doc version {filename} from node {node_id}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        return str(filepath)

    def diff_docs(self, node1_id, node2_id):
        import subprocess
        import tempfile
        if node1_id not in self.data or node2_id not in self.data:
            raise ValueError("Node IDs not found")
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1, tempfile.NamedTemporaryFile(mode="w",
                                                                                                    delete=False) as f2:
            f1.write(self.data[node1_id]["response"])
            f2.write(self.data[node2_id]["response"])
            f1_path, f2_path = f1.name, f2.name

        result = subprocess.run(["git", "diff", "--no-index", f1_path, f2_path], capture_output=True, text=True)
        return result.stdout.strip()

    def get_inline_diff(self, node_id):
        import subprocess
        import tempfile

        node = self.data.get(node_id)
        parent_id = node.get("parent_id") if node else None
        if not node or not parent_id or parent_id not in self.data:
            return None

        parent_text = self.data[parent_id]["response"]
        current_text = node["response"]

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1, tempfile.NamedTemporaryFile(mode="w",
                                                                                                    delete=False) as f2:
            f1.write(parent_text)
            f2.write(current_text)
            f1_path, f2_path = f1.name, f2.name

        result = subprocess.run(["git", "diff", "--no-index", f1_path, f2_path], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode in (0, 1) else None

    def export_version_graph(self, filename):
        lines = ["graph TD"]
        for node_id, node in self.data.items():
            if node.get("type") != "doc":
                continue
            label = node.get("filename", "doc.md").replace('"', "'")
            lines.append(f'{node_id}["{node_id}: {label}"]')

        for node_id, node in self.data.items():
            if node.get("type") != "doc":
                continue
            parent = node.get("parent_id")
            if parent and parent in self.data and self.data[parent].get("type") == "doc":
                lines.append(f"{parent} --> {node_id}")
            for cited in node.get("citations", []):
                if cited in self.data and self.data[cited].get("type") == "doc":
                    lines.append(f"{node_id} -.-> {cited}")

        output_path = Path("data") / filename
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        print(f"Exported document version graph to {output_path}")

    def export_citation_graph(self, filename):
        lines = ["graph TD"]
        for node_id, node in self.data.items():
            label = node.get("prompt", "").replace('"', "'").replace("\n", " ")[:60]
            lines.append(f'{node_id}["{node_id}: {label}"]')

        for node_id, node in self.data.items():
            if node.get("parent_id"):
                lines.append(f"{node['parent_id']} --> {node_id}")
            for cited in node.get("citations", []):
                if cited in self.data:
                    lines.append(f"{node_id} -.-> {cited}")

        output_path = Path("data") / filename
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        print(f"Exported full citation graph to {output_path}")

    def render_mermaid_to_svg(self, input_file, output_file):
        import subprocess
        input_path = Path("data") / input_file
        output_path = Path("data") / output_file
        cmd = ["npx", "mmdc", "-i", str(input_path), "-o", str(output_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        print(f"SVG rendered to {output_path}")

    def get_embedding(self, text):
        config = load_config()
        provider = config["provider"]
        print(f"[Embedding] Using {provider} (mock)")
        # Mock: hash text to 4-D vector for now
        return [float(hash(text + str(i)) % 1000) / 1000 for i in range(4)]

    def embed_node(self, node_id, dry_run=False):
        if node_id not in self.data:
            raise ValueError("Node not found")
        node = self.data[node_id]
        combined = f"{node.get('prompt', '')}\n{node.get('response', '')}"
        if dry_run:
            print(f"[DRY RUN] Would embed node {node_id}")
        else:
            node["embedding"] = self.get_embedding(combined)
        self._save()
        print(f"Embedded node {node_id}")

    def embed_subtree(self, root_id):
        if root_id not in self.data:
            raise ValueError("Root node not found")
        stack = [root_id]
        while stack:
            nid = stack.pop()
            self.embed_node(nid)
            stack.extend(self.data[nid].get("children", []))
        print(f"Embedded subtree rooted at {root_id}")

    def simsearch(self, query_text, top_k=3):
        query_vector = self.get_embedding(query_text)
        dim = len(query_vector)

        # Build FAISS index
        index = faiss.IndexFlatL2(dim)
        id_map = []
        vectors = []

        for node_id, node in self.data.items():
            id_map.append(node_id)
            vectors.append(np.array(node["embedding"], dtype=np.float32))

        if not vectors:
            print("No embedded nodes found.")
            return []

        index.add(np.stack(vectors))
        D, I = index.search(np.array([query_vector], dtype=np.float32), top_k)

        result_ids_scores = [
            (id_map[i], -D[0][j])  # negate distance to turn it into similarity
            for j, i in enumerate(I[0])
            if i < len(id_map)
        ]
        return result_ids_scores

    def embed_all(self, dry_run=False):
        count = 0
        for node_id in self.data:
            try:
                self.embed_node(node_id, dry_run=dry_run)
                count += 1
            except Exception:
                continue
        if not dry_run:
            print(f"Embedded {count} nodes.")

    def embed_summary(self, node_id):
        if node_id not in self.data:
            raise ValueError("Node not found")
        node = self.data[node_id]
        print(f"[{node_id}] {node.get('prompt', '')[:60]}")
        if "embedding" in node:
            print("Embedding:", [round(x, 3) for x in node["embedding"]])
        else:
            print("No embedding found.")

    def smart_cite(self, query_text, from_node_id=None, top_k=1):
        matches = self.simsearch(query_text, top_k=top_k)
        if from_node_id:
            for target in matches:
                self.add_citation(from_node_id, target)
            print(f"Smart-cited {len(matches)} nodes from {from_node_id}")
        return matches

    def ask_llm_direct(self, prompt):
        config = load_config()
        provider = config["provider"]
        model = config.get("openai_chat_model") if provider == "openai" else config.get("bedrock_model")
        print(f"[LLM] Using {provider}: {model}")
        return mock_llm_response(prompt)

    def smart_ask(self, query_text, from_node_id=None, top_k=3):
        """
        Run a smart-ask by semantically retrieving relevant nodes and generating an LLM answer.
        This constructs a RAG-style prompt using the top-K semantically similar nodes.

        Args:
            query_text (str): The user's question.
            from_node_id (str): The context node initiating the ask.
            top_k (int): Number of similar nodes to retrieve.

        Returns:
            str: The LLM-generated answer.
        """
        matches = self.simsearch(query_text, top_k=top_k)
        context_chunks = []
        citations = []

        for node_id, _score in matches:
            node = self.data.get(node_id, {})
            context = node.get("response") or node.get("prompt")
            if context:
                label = f"[CONTEXT from {node_id}]"
                context_chunks.append(label + "\n" + context.strip())
                citations.append(node_id)

        full_prompt = "\n\n".join(context_chunks)
        full_prompt += "\n\n[QUESTION]\n" + query_text.strip()

        if from_node_id is None or from_node_id not in self.data:
            answer = self.ask_llm_direct(full_prompt)
        else:
            answer = self.ask_llm_with_context(from_node_id, full_prompt)

        self._last_smart_ask = {
            "from_node_id": from_node_id,
            "question": query_text.strip(),
            "response": answer,
            "citations": citations,
        }

        return answer

    def promote_smart_ask(self, parent_id: str) -> str:
        """
        Promote the most recent smart-ask result into a new graph node.

        This function takes the cached smart-ask result — including the question, generated answer,
        and any cited nodes — and creates a new child node under the given `parent_id`. It copies
        the smart-ask content into the graph and establishes citation edges from the new node to
        its cited sources. If `auto_embed` is enabled, it will also embed the new node.

        Args:
            parent_id (str): The ID of the node that initiated the smart-ask.

        Returns:
            str: The node ID of the newly created promoted smart-ask node.

        Raises:
            ValueError: If no smart-ask has been performed yet or if it doesn't match the parent.
        """
        if self._last_smart_ask is None:
            raise ValueError("No smart-ask result available to promote.")

        data = self._last_smart_ask
        if data["from_node_id"] != parent_id:
            raise ValueError("Smart-ask result does not match current node.")

        prompt = data["question"]
        response = data["response"]
        citations = data.get("citations", [])

        node_id = self._generate_id()
        self.data[node_id] = {
            "id": node_id,
            "parent_id": parent_id,
            "prompt": prompt,
            "response": response,
            "children": [],
            "tags": ["smart-ask"]
        }

        self.data[parent_id]["children"].append(node_id)

        for cited_id in citations:
            self.add_citation(node_id, cited_id)

        config = load_config()
        if config.get("auto_embed", False):
            self.embed_node(node_id)

        self._save()
        return node_id

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
