import typer
from chatcli.core.graph import ConversationGraph

app = typer.Typer()
graph = ConversationGraph()
current_id = None
web_results = []


        elif command.startswith("search"):
            parts = command.split(" ", 1)
            if len(parts) != 2:
                print("Usage: search <keyword/tag>")
                continue
            matches = graph.search(parts[1])
            if not matches:
                print("No matches found.")
            else:
                print("Matches:")
                for line in graph.describe_nodes(matches):
                    print(" -", line)

        elif command.startswith("filter"):
            if not current_id:
                print("No active node.")
            else:
                parts = command.split()
                if len(parts) != 2:
                    print("Usage: filter cites|cited-by|related")
                else:
                    if parts[1] == "cites":
                        results = graph.filter_cites(current_id)
                    elif parts[1] == "cited-by":
                        results = graph.filter_cited_by(current_id)
                    elif parts[1] == "related":
                        results = graph.filter_related(current_id)
                    else:
                        print("Unknown filter type."); continue
                    print("Related nodes:")
                    for line in graph.describe_nodes(results):
                        print(" -", line)

        elif command.startswith("show-cites"):
            if not current_id:
                print("No active node.")
            else:
                cites = graph.get_citations(current_id)
                cited_by = graph.get_cited_by(current_id)
                print(f"Cites: {', '.join(cites) if cites else 'None'}")
                print(f"Cited by: {', '.join(cited_by) if cited_by else 'None'}")