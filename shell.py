"""Provides a configurable shell prompt with tab complete."""

import os
import os.path
import readline
import atexit


class Shell:
    """Implement the configurable shell."""

    # pylint: disable=too-few-public-methods

    class Color:
        """Define shell colors."""

        BLACK = "\033[30m"
        DARKRED = "\033[31m"
        DARKGREEN = "\033[32m"
        ORANGE = "\033[33m"
        NAVY = "\033[34m"
        DARKMAGENTA = "\033[35m"
        CYAN = "\033[36m"
        DARKGRAY = "\033[1;30m"
        LIGHTGRAY = "\033[37m"
        RED = "\033[1;31m"
        GREEN = "\033[1;32m"
        YELLOW = "\033[1;33m"
        BLUE = "\033[1;34m"
        MAGENTA = "\033[1;35m"
        LIGHTCYAN = "\033[1;36m"
        WHITE = "\033[1;37m"
        RESET = "\033[0m"

    def __tab_complete(self, _, state):
        """Return the next possible (state) command represented by text."""
        path, key, data = self.__get_dict_entry(readline.get_line_buffer())
        key = key[0] if key else ""
        if isinstance(data, tuple):
            values = data[1]
        if isinstance(data, dict):
            values = list(data.keys())
        valid = [
            option
            for option in values
            if option.startswith(key) and option not in path
        ]
        return valid[state] + " " if state < len(valid) else None

    def update_command(self, key, options, function=None):
        """Update options for a command."""
        *key, cmd = key.split(" ")
        path, _, data = self.__get_dict_entry(" ".join(key))
        path = " ".join(path)
        if function is None:
            function, _ = data[cmd]
        data[cmd] = (function, options)

    def __init__(self, name, commands, **options):
        """Initialize the shell for the given commands."""
        self.__name = name
        self.__commands = commands
        hist_default = os.path.join(os.environ["HOME"], ".%s_history" % name)
        self.__history = options.get("history_file", hist_default)
        delims = readline.get_completer_delims().replace("-", "")
        readline.set_completer_delims(delims)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.__tab_complete)
        atexit.register(readline.write_history_file, self.__history)
        try:
            readline.read_history_file(self.__history)
        except FileNotFoundError:
            pass
        readline.set_history_length(options.get("history_length", 1000))
        self.__prompt = options.get("prompt", ">")
        self.colors = {
            k[:-6]: v for k, v in options.items() if k.endswith("_color")
        }

    def __iter__(self):
        """Return the shell object as an iterator."""
        return self

    def __get_dict_entry(self, key):
        parts = key.strip().split(" ")
        data = self.__commands
        path = []
        for part in parts:
            if not part or part not in data:
                break
            data = data[part]
            path.append(part)
            if not isinstance(data, dict):
                break
        return path, parts[len(path) :], data

    def __next__(self):
        """Run the shell until input ends."""
        try:
            function = ""
            while not callable(function):
                prompt_color = self.colors.get("prompt") or ""
                prompt = "%s%s%s" % (
                    prompt_color,
                    self.__prompt,
                    Shell.Color.RESET,
                )
                command = input(prompt)
                _, args, (function, *_) = self.__get_dict_entry(command)
            return (function, args or [])
        except EOFError:
            raise StopIteration()
        except KeyboardInterrupt:
            raise StopIteration()
