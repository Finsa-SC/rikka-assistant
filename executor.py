import shlex
import re

class CommandExecutor:
    def __init__(self):
        self.denied_command = ["rm", "shutdown", "reboot", "poweroff", "mkfs", "dd"]
        self.pattern = r"\[<.+?>\]"

    def extract_command(self, text: str) -> tuple[str, list[str]]:
        extract_cmds = re.findall(self.pattern, text)
        clean_text = re.sub(self.pattern, "", text).strip()

        clean_text, [cmd.strip() for cmd in extract_cmds]

    def filter_command(self, command: str) -> bool:
        if not command:
            return False

        try:
            parts = shlex.split(command)
            if not parts:
                return False

            base_command = parts[0].lower()

            if base_command in self.denied_command:
                return False

            return True
        except:
            return False