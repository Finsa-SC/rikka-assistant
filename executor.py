import shlex
import re
import subprocess

from logger import get_logger

log = get_logger("Executor")

class CommandExecutor:
    def __init__(self):
        self.denied_command = ["rm", "shutdown", "reboot", "poweroff", "mkfs", "dd"]
        self.pattern = r"\[!([\s\S]+?)\]"
        self.bg_pattern = r"\[~([\s\S]+?)~\]"

    def extract_commands(self, text: str) -> tuple[str, list[str]]:
        extract_cmds = re.findall(self.pattern, text)
        clean_text = re.sub(self.pattern, "", text).strip()

        return clean_text, [cmd.strip() for cmd in extract_cmds]

    def filter_commands(self, command: str) -> bool:
        if not command:
            return False
        first_word = command.strip().split()[0].lower()
        return first_word not in self.denied_command

    def execute_commands(self, command: str) -> str:
        if not self.filter_commands(command):
            log.warning(f"Forbidden executing: {command}")
            return f"Forbidden command {command}"
        try:
            result = subprocess.run(
                command,
                timeout=20,
                text=True,
                capture_output=True,
                shell=True,
            )

            if result.returncode == 0:
                return result.stdout.strip() if result.stdout.strip() else "Success without output"
            else:
                log.error(f"Error occured while executing command")
                return f"Error occured while executing command: \n{result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            log.error(f"Command timeout while it is running")
            return f"Command timeout while it is running"
        except Exception as e:
            log.error(f"Error occured while executing command: {e}")
            return f"Error occured while executing command: {e}"


if __name__ == "__main__":
    executor = CommandExecutor()

    # Contoh teks tiruan dari respon Nino
    sample_ai_response = "I will check the kernel version first [!<uname -a>], then I will clean the log directory [!<rm -rf /var/log/test.log>]"

    print("=== TEST EXTRAK ===")
    c_text, cmds = executor.extract_commands(sample_ai_response)
    print(f"Clean Text: {c_text}")
    print(f"Extracted Commands: {cmds}\n")

    print("=== TEST EKSEKUSI ===")
    for c in cmds:
        print(f"Executing '{c}'...")
        output = executor.execute_commands(c)
        print(f"Result:\n{output}\n")
