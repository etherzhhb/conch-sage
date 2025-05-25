import typer
from chatcli.core.graph import ConversationGraph

app = typer.Typer()
graph = ConversationGraph()
current_id = None
web_results = []


        elif command.startswith("import-doc"):
            parts = command.split(" ", 1)
            if len(parts) != 2:
                print("Usage: import-doc <filename>")
                continue
            try:
                new_id = graph.import_doc(parts[1], current_id)
                print(f"Imported as node {new_id}")
            except Exception as e:
                print(f"Import failed: {e}")

        elif command.startswith("improve-doc"):
            if not current_id:
                print("No active node.")
                continue
            try:
                new_id = graph.improve_doc(current_id)
                print(f"Improved version saved as node {new_id}")
            except Exception as e:
                print(f"Improve failed: {e}")

        elif command.startswith("save-doc"):
            parts = command.split(" ", 1)
            if not current_id or len(parts) != 2:
                print("Usage: save-doc <output_filename>")
                continue
            try:
                saved_path = graph.save_doc(current_id, parts[1])
                print(f"Saved to {saved_path}")
            except Exception as e:
                print(f"Save failed: {e}")

        elif command.startswith("version-doc"):
            if not current_id:
                print("No active node.")
                continue
            try:
                saved_path = graph.save_doc_version(current_id)
                print(f"Committed to git: {saved_path}")
            except Exception as e:
                print(f"Versioning failed: {e}")

        elif command.startswith("diff-doc"):
            parts = command.split()
            if len(parts) != 3:
                print("Usage: diff-doc <node1> <node2>")
                continue
            try:
                diff = graph.diff_docs(parts[1], parts[2])
                print(diff)
            except Exception as e:
                print(f"Diff failed: {e}")