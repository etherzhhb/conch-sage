import cmd
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from chatcli.core.graph import ConversationGraph

COMMANDS = [
    "new", "reply", "view", "tree", "import", "improve", "save", "websearch",
    "saveurl", "citeurl", "ask", "embed_summary", "embed_node", "embed_all",
    "embed_subtree", "simsearch", "smart_ask", "promote_smart_ask", "exit"
]

class ChatCLIShell(cmd.Cmd):
    prompt = "chatcli> "

    def __init__(self):
        super().__init__()
        self.graph = ConversationGraph()
        self.current_id = None
        self.web_results = []
        self.session = PromptSession(
            history=FileHistory(".chatcli_history"),
            completer=WordCompleter(COMMANDS, ignore_case=True),
        )

    def cmdloop(self, intro=None):
        print("Welcome to Conch Sage. Type 'exit' to quit.")
        while True:
            try:
                line = self.session.prompt(self.prompt)
                if not line.strip():
                    continue
                stop = self.onecmd(line)
                if stop:
                    break
            except (EOFError, KeyboardInterrupt):
                print()
                break
    def default(self, line):
        print(f"*** Unknown syntax: {line}")

    def do_exit(self, arg):
        return True

    def do_new(self, arg):
        self.current_id = self.graph.new(arg)
        print(f"New node: {self.current_id}")

    def do_reply(self, arg):
        if not self.current_id:
            print("No current node.")
            return
        self.current_id = self.graph.reply(self.current_id, arg)
        print(f"Replied with node: {self.current_id}")

    def do_view(self, arg):
        if not self.current_id:
            print("No current node.")
            return
        node = self.graph.get(self.current_id)
        print(f"[{node['id']}] {node['prompt']}\n{node['response']}")

    def do_tree(self, arg):
        self.graph.print_tree(self.current_id or "root")

    def do_import(self, arg):
        try:
            new_id = self.graph.import_doc(arg, self.current_id)
            print(f"Imported {arg} as {new_id}")
        except Exception as e:
            print(f"Import failed: {e}")

    def do_improve(self, arg):
        try:
            new_id = self.graph.improve_doc(self.current_id)
            self.current_id = new_id
            print(f"Improved doc as {new_id}")
        except Exception as e:
            print(f"Improve failed: {e}")

    def do_save(self, arg):
        if not self.current_id:
            print("No active node.")
            return
        self.graph.save_doc(self.current_id, arg)
        print(f"Saved to {arg}")

    def do_websearch(self, arg):
        self.web_results = self.graph.mock_websearch(arg)
        for i, r in enumerate(self.web_results):
            print(f"[{i}] {r['title']}\n    {r['snippet']}\n    {r['url']}")

    def do_saveurl(self, arg):
        try:
            idx = int(arg)
            nid = self.graph.save_web_result(self.web_results[idx], self.current_id)
            print(f"Saved URL result as node {nid}")
        except Exception as e:
            print(f"Failed to save URL: {e}")

    def do_citeurl(self, arg):
        try:
            idx = int(arg)
            nid = self.graph.save_web_result(self.web_results[idx])
            self.graph.add_citation(self.current_id, nid)
            print(f"Cited node {nid}")
        except Exception as e:
            print(f"Failed to cite URL: {e}")

    def do_embed_summary(self, arg):
        try:
            self.graph.embed_summary(arg or self.current_id)
        except Exception as e:
            print(f"Summary failed: {e}")

    def do_embed_node(self, arg):
        try:
            dry_run = "--dry-run" in arg
            node_id = arg.replace("--dry-run", "").strip() or self.current_id
            self.graph.embed_node(node_id, dry_run=dry_run)
        except Exception as e:
            print(f"Embed failed: {e}")

    def do_embed_all(self, arg):
        try:
            self.graph.embed_all("--dry-run" in arg)
        except Exception as e:
            print(f"Embed-all failed: {e}")

    def do_embed_subtree(self, arg):
        try:
            dry_run = "--dry-run" in arg
            node_id = arg.replace("--dry-run", "").strip() or self.current_id
            self.graph.embed_subtree(node_id, dry_run=dry_run)
        except Exception as e:
            print(f"Embed subtree failed: {e}")

    def do_simsearch(self, arg):
        query = arg.strip()
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

    def do_ask(self, arg):
        if not self.current_id:
            print("No current node.")
            return
        print(self.graph.ask_llm_with_context(self.current_id, arg))

    def do_smart_ask(self, arg):
        print(self.graph.smart_ask(arg, from_node_id=self.current_id))

    def do_promote_smart_ask(self, arg):
        new_id = self.graph.promote_smart_ask(self.current_id)
        self.current_id = new_id
        print(f"Promoted to new node {new_id}")