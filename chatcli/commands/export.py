import typer
from chatcli.core.graph import ConversationGraph

app = typer.Typer()
graph = ConversationGraph()
current_id = None
web_results = []


        elif command.startswith("export-version-graph"):
            parts = command.split(" ", 1)
            if len(parts) != 2:
                print("Usage: export-version-graph <filename.mmd>")
                continue
            try:
                graph.export_version_graph(parts[1])
            except Exception as e:
                print(f"Export failed: {e}")

        elif command.startswith("export-citation-graph"):
            parts = command.split(" ", 1)
            if len(parts) != 2:
                print("Usage: export-citation-graph <filename.mmd>")
                continue
            try:
                graph.export_citation_graph(parts[1])
            except Exception as e:
                print(f"Export failed: {e}")

        elif command.startswith("render-svg"):
            parts = command.split()
            if len(parts) != 3:
                print("Usage: render-svg <input.mmd> <output.svg>")
                continue
            try:
                graph.render_mermaid_to_svg(parts[1], parts[2])
            except Exception as e:
                print(f"SVG render failed: {e}")