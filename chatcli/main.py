# chatcli/main.py

from chatcli.shell import ChatCLIShell

def main():
    shell = ChatCLIShell()
    shell.cmdloop()
