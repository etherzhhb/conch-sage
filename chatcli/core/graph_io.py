# chatcli/core/graph_io.py

import json
from pathlib import Path

from chatcli.core.config import load_config

def load_graph_state(graph, path=None):
    if graph._in_memory:
        return {}, None

    path = path or graph._storage_path
    if not Path(path).exists():
        return {}, None  # New file — nothing to load

    try:
        with open(path, "r") as f:
            payload = json.load(f)

        if not isinstance(payload, dict) or "nodes" not in payload:
            raise ValueError("Invalid file format: missing 'nodes'")

        return payload["nodes"], payload.get("last_smart_ask")
    except Exception as e:
        print(f"Warning: failed to load {path}: {e}")
        return {}, None


def save_to_file(graph, filename, verbose=False):
    """Save full graph state (nodes + last_smart_ask) to JSON file."""
    if graph._in_memory:
        return

    path = graph._save_dir / filename
    with open(path, "w") as f:
        json.dump({
            "nodes": graph.data,
            "last_smart_ask": graph._last_smart_ask
        }, f, indent=2)

    if verbose:
        print(f"Saved to {path}")


def import_from_file(graph, filename, dry_run_embedding=False):
    """
    Import a full conversation graph (including smart-ask context) from a JSON file.

    Args:
        filename (str): File name relative to the export directory.
        dry_run_embedding (bool): If True, skip actual embedding.
    """
    filepath = graph._save_dir / filename
    graph._data, graph._last_smart_ask = load_graph_state(graph, path=filepath)

    if not graph.data:
        print(f"No data imported from {filepath}")
        return

    config = load_config()
    if config.get("auto_embed", False):
        for node_id in graph.data:
            graph.embed_node(node_id, dry_run=dry_run_embedding)

    graph._save()
    print(f"Imported full graph from {filepath}")

def import_doc(graph, filepath, current_id=None, dry_run_embedding=False, truncate: int | None = None):
    """Import a markdown/rst file into the graph as a new node."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    content = path.read_text()

    if truncate is not None:
        if truncate <= 0:
            raise ValueError("truncate must be a positive integer")
        content = content[:truncate]

    node_id = graph._generate_id()
    graph.data[node_id] = {
        "id": node_id,
        "type": "doc",
        "filename": path.name,
        "parent_id": current_id,
        "prompt": f"Imported document: {path.name}",
        "response": content,
        "children": [],
        "tags": ["doc"]
    }
    if current_id:
        graph.data[current_id]["children"].append(node_id)
    config = graph._config if hasattr(graph, "_config") else {}
    if config.get("auto_embed", False):
        graph.embed_node(node_id, dry_run=dry_run_embedding)
    graph._save()
    return node_id

def save_doc(graph, node_id, filepath):
    node = graph.data.get(node_id)
    if not node:
        raise ValueError("Node not found")
    with open(filepath, "w") as f:
        f.write(node.get("response", ""))
    print(f"Saved node {node_id} to {filepath}")
    return filepath


def save_doc_version(graph, node_id, repo_path):
    """
    Save the response of the given node to a Markdown file and commit it to a Git repository.

    If the target directory is not already a Git repository, it will be initialized.
    The filename is derived from the node ID and ends in '.md'.

    Args:
        node_id (str): ID of the node to save.
        repo_path (str or Path): Path to the Git repository directory.
    """
    from pathlib import Path
    import subprocess

    repo_path = Path(repo_path)
    filepath = repo_path / f"{node_id}_doc.md"
    content = graph.data[node_id]["response"]

    filepath.write_text(content, encoding="utf-8")

    # Initialize Git repo if needed
    if not (repo_path / ".git").exists():
        subprocess.run(["git", "init"], cwd=repo_path, check=True)

    # Add and commit the file
    subprocess.run(["git", "add", str(filepath.name)], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Save version of {filepath.name}"],
        cwd=repo_path,
        check=True
    )

def diff_doc_versions(graph, node_id, repo_path):
    """
    Diff the last two Git-committed versions of the document corresponding to node_id.
    Returns a unified diff string.
    """
    import subprocess
    from pathlib import Path

    repo_path = Path(repo_path)
    filepath = f"{node_id}_doc.md"

    # Ensure repo exists
    if not (repo_path / ".git").exists():
        raise RuntimeError(f"{repo_path} is not a Git repository")

    # Run git log to get the last two commits for the file
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", "-n", "2", "--pretty=format:%H", "--", filepath],
        capture_output=True, text=True, check=True
    )
    commits = result.stdout.strip().splitlines()
    if len(commits) < 2:
        raise RuntimeError("Not enough commits to perform diff")

    rev1, rev2 = commits[1], commits[0]  # earlier → later

    # Run the diff between two versions
    result = subprocess.run(
        ["git", "-C", str(repo_path), "diff", rev1, rev2, "--", filepath],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

def diff_docs(graph, node1_id, node2_id):
    import subprocess
    import tempfile
    if node1_id not in graph.data or node2_id not in graph.data:
        raise ValueError("Node IDs not found")
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1, tempfile.NamedTemporaryFile(mode="w",
                                                                                                delete=False) as f2:
        f1.write(graph.data[node1_id]["response"])
        f2.write(graph.data[node2_id]["response"])
        f1_path, f2_path = f1.name, f2.name

    result = subprocess.run(["git", "diff", "--no-index", f1_path, f2_path], capture_output=True, text=True)
    return result.stdout.strip()

def load_from_file(graph, filename, dry_run_embedding=False):
    """Load graph from disk."""
    path = graph._save_dir / filename
    if not path.exists():
        print(f"File {filename} not found in {graph._save_dir}")
        return
    with open(path, "r") as f:
        obj = json.load(f)
        graph.data = obj.get("nodes", {})
        graph._last_smart_ask = obj.get("last_smart_ask", None)
    if graph._config.get("auto_embed", False):
        for node_id in graph.data:
            graph.embed_node(node_id, dry_run=dry_run_embedding)
    graph._save()
    print(f"Loaded from {path}")


def export_mermaid(graph, filename):
    lines = ["graph TD"]
    for node_id, node in graph.data.items():
        label = node['prompt'].replace('"', "'").replace("\n", " ")[:50]
        lines.append(f'{node_id}["{label}"]')
    for node_id, node in graph.data.items():
        for child_id in node.get("children", []):
            lines.append(f"{node_id} --> {child_id}")
        for cited_id in node.get("citations", []):
            lines.append(f"{node_id} -.-> {cited_id}")
    filepath = graph._save_dir / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        f.write("\n".join(lines))
    print(f"Exported graph to {filepath}")
