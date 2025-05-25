import typer
from chatcli.core.graph import ConversationGraph

app = typer.Typer()
graph = ConversationGraph()
current_id = None
web_results = []


        elif command.startswith("new "):
            prompt = command[4:].strip()
            node_id = graph.new_thread(prompt)
            current_id = node_id
            print(f"[{node_id}] Started new thread")

        elif command.startswith("reply "):
            if not current_id:
                print("No active thread. Use `new` first.")
                continue
            prompt = command[6:].strip()
            node_id = graph.reply(current_id, prompt)
            current_id = node_id
            print(f"[{node_id}] Replied to {graph.get(node_id)['parent_id']}")
        elif command == "view":
            if not current_id:
                print("No active node.")
                continue
            node = graph.get(current_id)
            print(f"[{node['id']}] {node['prompt']}\n{node['response']}")
            if node.get('type') == 'doc':
                diff = graph.get_inline_diff(current_id)
                if diff:
                    print("\n[Inline diff with parent version]\n" + diff)
            if 'comment' in node:
                print(f"Comment: {node['comment']}")
            if 'tags' in node and node['tags']:
                print(f"Tags: {', '.join(node['tags'])}")
            if 'citations' in node:
                print("Cites:")
                for cid in node['citations']:
                    print(" -", graph.preview_node(cid), f"→ Type: goto {cid}")
            continue
            if not current_id:
                print("No active node.")
                continue
            node = graph.get(current_id)
            print(f"[{node['id']}] {node['prompt']}\n{node['response']}")
            if node.get('type') == 'doc':
                diff = graph.get_inline_diff(current_id)
                if diff:
                    print("\n[Inline diff with parent version]\n" + diff)
            if 'comment' in node:
                print(f"Comment: {node['comment']}")
            if 'tags' in node and node['tags']:
                print(f"Tags: {', '.join(node['tags'])}")
        elif command == "back":
            if not current_id:
                print("No active node.")
                continue
            parent_id = graph.get(current_id)["parent_id"]
            if not parent_id:
                print("Already at root.")
                continue
            current_id = parent_id
            print(f"Moved to parent [{current_id}]")
        elif command == "tree":
            if not current_id:
                print("No active node.")
                continue
            root = current_id
            while graph.get(root)["parent_id"]:
                root = graph.get(root)["parent_id"]
            graph.print_tree(root)
        elif command == "edit":
            if not current_id:
                print("No active node.")
                continue
            node = graph.get(current_id)
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
                tf.write(node["response"].encode())
                tf.flush()
                os.system(f"{os.environ.get('EDITOR', 'nano')} {tf.name}")
                tf.seek(0)
                new_response = tf.read().decode()
            graph.edit_response(current_id, new_response)
            print("Response updated.")