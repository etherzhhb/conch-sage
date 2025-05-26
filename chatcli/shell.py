from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
import cmd
from chatcli.core.graph import ConversationGraph

COMMANDS = [
    "new", "reply", "view", "tree", "import", "improve",
    "save", "websearch", "saveurl", "citeurl", "ask", "exit"
]

class ChatCLIShell:
    def __init__(self):
        self.graph = ConversationGraph()
        self.current_id = None
        self.web_results = []
        self.session = PromptSession(
            history=FileHistory(".chatcli_history"),
            completer=WordCompleter(COMMANDS, ignore_case=True),
        )

    def run(self):
        print("Welcome to chatcli shell. Type 'exit' to quit.")
        while True:
            try:
                line = self.session.prompt("chatcli> ")
            except (EOFError, KeyboardInterrupt):
                break
            if not line.strip():
                continue
            if not self.dispatch(line):
                break

    def dispatch(self, line):
        parts = line.strip().split(" ", 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""


    def do_simsearch(self, line):
        """simsearch <query> -- perform a semantic search"""
        query = line.strip()
        if not query:
            print("Usage: simsearch <query>")
            return
        results = self.graph.simsearch(query)
        if not results:
            print("No similar nodes found.")
            return
        for node_id, score in results:
            prompt = self.graph.data[node_id].get('prompt', '')
            print(f"{node_id[:8]}  {score:.2f}  {prompt[:60]}")
        if cmd == "exit":
            return False
        elif cmd == "new":
            self.current_id = self.graph.new(arg)
            print(f"New node: {self.current_id}")
        elif cmd == "reply":
            if not self.current_id:
                print("No current node."); return True
            self.current_id = self.graph.reply(self.current_id, arg)
            print(f"Replied with node: {self.current_id}")
        elif cmd == "view":
            if not self.current_id:
                print("No current node."); return True
            node = self.graph.get(self.current_id)
            print(f"[{node['id']}] {node['prompt']}\n{node['response']}")
        elif cmd == "tree":
            self.graph.print_tree(self.current_id or "root")
        elif cmd == "import":
            try:
                new_id = self.graph.import_doc(arg, self.current_id)
                print(f"Imported {arg} as {new_id}")
            except Exception as e:
                print(f"Import failed: {e}")
        elif cmd == "improve":
            try:
                new_id = self.graph.improve_doc(self.current_id)
                self.current_id = new_id
                print(f"Improved doc as {new_id}")
            except Exception as e:
                print(f"Improve failed: {e}")
        elif cmd == "save":
            if not self.current_id:
                print("No active node."); return True
            self.graph.save_doc(self.current_id, arg)
            print(f"Saved to {arg}")
        elif cmd == "websearch":
            self.web_results = self.graph.mock_websearch(arg)
            for i, r in enumerate(self.web_results):
                print(f"[{i}] {r['title']}\n    {r['snippet']}\n    {r['url']}")
        elif cmd == "saveurl":
            try:
                idx = int(arg)
                nid = self.graph.save_web_result(self.web_results[idx], self.current_id)
                print(f"Saved URL result as node {nid}")
            except Exception as e:
                print(f"Failed to save URL: {e}")
        elif cmd == "citeurl":
            try:
                idx = int(arg)
                nid = self.graph.save_web_result(self.web_results[idx])
                self.graph.add_citation(self.current_id, nid)
                print(f"Cited node {nid}")
            except Exception as e:
                print(f"Failed to cite URL: {e}")
        elif cmd == "embed-summary":
            try:
                self.graph.embed_summary(arg or self.current_id)
            except Exception as e:
                print(f"Summary failed: {e}")
        elif cmd == "embed-node":
            try:
                self.graph.embed_node(arg.replace("--dry-run", "").strip() or self.current_id, "--dry-run" in arg)
            except Exception as e:
                print(f"Embed failed: {e}")
        elif cmd == "embed-all":
            try:
                self.graph.embed_all("--dry-run" in arg)
            except Exception as e:
                print(f"Embed-all failed: {e}")
        elif cmd == "embed-subtree":
            try:
                self.graph.embed_subtree(arg.replace("--dry-run", "").strip() or self.current_id, "--dry-run" in arg)
            except Exception as e:
                print(f"Embed subtree failed: {e}")
        elif cmd == "ask":
            if not self.current_id:
                print("No current node."); return True
            print(self.graph.ask_llm_with_context(self.current_id, arg))
        else:
            print(f"Unknown command: {cmd}")
        return True