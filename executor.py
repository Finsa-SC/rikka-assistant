import re

class CommandExecutor:
    def __init__(self):
        self.denied_command = ["rm", "shutdown", "reboot", "poweroff", "mkfs", "dd"]
        self.pattern = r"\[<.+?>\]"

    def extract_command(self, text: str) -> tuple[str, list[str]]:
        extract_cmds = re.findall(self.pattern, text)
        clean_text = re.sub(self.pattern, "", text).strip()

        clean_text, [cmd.strip() for cmd in extract_cmds]
