import re
import subprocess
from time import sleep

from logger import get_logger

log = get_logger("Executor")

class CommandExecutor:
    def __init__(self):
        self.denied_command = ["rm", "shutdown", "reboot", "poweroff", "mkfs", "dd"]
        self.fg_pattern = r"<RUN>([\s\S]+?)<\/RUN>"
        self.bg_pattern = r"<SPAWN>([\s\S]+?)<\/SPAWN>"

    def extract_commands(self, text: str) -> tuple[str, list[str]]:
        if not text:
            return "", []

        fg_cmds = re.findall(self.fg_pattern, text)
        bg_cmds = re.findall(self.bg_pattern, text)

        clean_text = re.sub(self.fg_pattern, "", text)
        clean_text = re.sub(self.bg_pattern, "", clean_text).strip()

        command = []
        for cmd in fg_cmds:
            command.append({"cmd": cmd.strip(), "mode": "foreground"})
        for cmd in bg_cmds:
            command.append({"cmd": cmd.strip(), "mode": "background"})

        return clean_text, command

    def filter_commands(self, command: str) -> bool:
        if not command:
            return False
        first_word = command.strip().split()[0].lower()
        return first_word not in self.denied_command

    def execute_commands(self, cmd_obj: dict) -> str:
        command = cmd_obj["cmd"]
        mode = cmd_obj.get("mode", "foreground")

        if not self.filter_commands(command):
            log.warning(f"Forbidden executing: {command}")
            return f"Forbidden command {command}"

        if mode == "background":
            return self._run_detached(command)
        else:
            return self._run_foreground(command=command)

    @staticmethod
    def _run_detached(command: str, check_delay: float = 1.5) -> str:
        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                start_new_session=True,
            )
            sleep(check_delay)
            poll = proc.poll()
            if poll is not None and poll != 0:
                stderr = proc.stderr.read().decode(errors='replace').strip()
                log.error(f"Detached process crashed (exit {poll}: {stderr}")
                return f"Error (exit {poll}:\n{stderr}"

            log.info(f"Launched in background: {command}")
            return f"Launch in background (PID {proc.pid})"
        except Exception as e:
            log.error(f"Error while launching detached command: {e}")
            return f"Error launching command: {e}"

    @staticmethod
    def _run_foreground(command: str, timeout: float = 60) -> str:
        try:
            result = subprocess.run(
                command,
                timeout=timeout,
                text=True,
                shell=True,
                capture_output=True
            )

            return (
                f"Command: {command}\n"
                f"Exit code: {result.returncode}\n"
                f"Stdout:\n{result.stdout.strip()}\n"
                f"Error:\n{result.stderr.strip()}"
            )
        except subprocess.TimeoutExpired:
            log.error(f"Command timeout: {command}")
            return f"Command timed out after {timeout}s"
        except Exception as e:
            log.error(f"Error: {e}")
            return f"Error: {e}"

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
