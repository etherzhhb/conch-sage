import typer
from chatcli.core.graph import ConversationGraph

app = typer.Typer()
graph = ConversationGraph()
current_id = None
web_results = []


        elif command.startswith("websearch"):
            parts = command.split(" ", 1)
            if len(parts) != 2:
                print("Usage: websearch <query>")
                continue
            web_results.clear()
            results = graph.mock_websearch(parts[1])
            web_results.extend(results)
            for i, r in enumerate(results):
                print(f"[{i}] {r['title']}\n    {r['snippet']}\n    {r['url']}")

        elif command.startswith("save-url"):
            if not web_results:
                print("No web results loaded. Run websearch first.")
            else:
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    idx = int(parts[1])
                    if 0 <= idx < len(web_results):
                        node_id = graph.save_web_result(web_results[idx], current_id)
                        print(f"Saved as node {node_id}")
                    else:
                        print("Invalid index")
                else:
                    print("Usage: save-url <index>")

        elif command.startswith("cite-url"):
            if not current_id:
                print("No active node.")
            elif not web_results:
                print("No web results loaded. Run websearch first.")
            else:
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    idx = int(parts[1])
                    if 0 <= idx < len(web_results):
                        node_id = graph.save_web_result(web_results[idx])
                        graph.add_citation(current_id, node_id)
                        print(f"Cited web result via node {node_id}")
                    else:
                        print("Invalid index")
                else:
                    print("Usage: cite-url <index>")