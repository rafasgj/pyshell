"""Example to create an iteractive shell."""

import os
import sys
from shell import Shell


def list_dir(_):
    """List directories and files."""

    def print_entries(entries, color):
        if entries:
            letters = 0
            for entry in entries:
                word = entry.name
                size = len(word)
                if letters + size > 79:
                    print()
                    letters = 0
                print("%s%s%s" % (color, word, Shell.Color.RESET), end=" ")
                letters += size
            print()

    current_dir = os.getcwd()
    data = list(os.scandir(current_dir))
    print_entries([e for e in data if e.is_dir()], Shell.Color.BLUE)
    print_entries([e for e in data if e.is_file()], Shell.Color.YELLOW)


def change_dir(shell, *args, **_):
    """Change current directory."""
    current_dir = os.getcwd()
    path = os.path.join(current_dir, args[0])
    os.chdir(path)
    shell.update_command("cd", get_current_dir_list())


def get_current_dir_list():
    """Get a list of directories in the current directory."""
    return [e.name for e in os.scandir(os.getcwd()) if e.is_dir()]


def exec_inner(_, *args):
    """Execute `inner` command."""
    print("INNER:", args)


def exec_another(_, *args):
    """Execute `anether` command."""
    print("ANOTHER:", args)


def main():
    """Program entry point."""
    commands = {
        "level": {
            "multi": (exec_inner, ["inner", "other"]),
            "another": (exec_another, ),
        },
        "ls": (list_dir,),
        "cd": (change_dir, get_current_dir_list()),
        "exit": (sys.exit,),
    }

    shell = Shell(
        "test",
        commands,
        history_file=".test_history",
        prompt="> ",
        prompt_color=Shell.Color.RED
    )
    for cmd, args in shell:
        cmd(shell, *args)
    print()


if __name__ == "__main__":
    main()
