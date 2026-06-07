import shlex
import re
import subprocess

from logger import get_logger

log = get_logger("Executor")

class CommandExecutor:
    def __init__(self):
        self.denied_command = ["rm", "shutdown", "reboot", "poweroff", "mkfs", "dd"]
        self.fg_pattern = r"\[!([\s\S]+?)\]"
        self.bg_pattern = r"\[~([\s\S]+?)~\]"

    def extract_commands(self, text: str) -> tuple[str, list[str]]:
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
            return self._run_foreground(command)

    @staticmethod
    def _run_detached(self, command: str) -> str:
        try:
            log.info(f"Launched in background: {command}")
            proc = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
                start_new_session=True,
            )
            return f"Launch in background (PID {proc.pid})"
        except Exception as e:
            log.error(f"Error while launching detached command: {e}")
            return f"Error launching command: {e}"

    @staticmethod
    def _run_foreground(self, command: str, timeout: float = 60) -> str:
        try:
            result = subprocess.run(
                command,
                timeout=timeout,
                text=True,
                shell=True,
                capture_output=True
            )
            if result.returncode == 0:
                return result.stdout.strip() if result.stdout.strip() else "Success without output"
            else:
                log.error(f"Command error: {result.stderr}")
                return f"Error:\n{result.stderr.strip()}"
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
