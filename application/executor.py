import re, json, subprocess
from datetime import datetime
from time import sleep

from logger import get_logger
from monitoring import Scheduler

log = get_logger("Executor")

class CommandExecutor:
    def __init__(self, schedule: Scheduler):
        self.scheduler = schedule

        self.denied_command = ["rm", "shutdown", "reboot", "poweroff", "mkfs", "dd"]
        self.fg_pattern = r"<RUN>([\s\S]+?)<\/RUN>"
        self.bg_pattern = r"<SPAWN>([\s\S]+?)<\/SPAWN>"
        self.schedule_pattern = r"<SCHEDULE>([\s\S]+?)<\/SCHEDULE>"

    def extract_commands(self, text: str) -> tuple[str, list[dict]]:
        if not text:
            return "", []

        fg_cmds = re.findall(self.fg_pattern, text)
        bg_cmds = re.findall(self.bg_pattern, text)
        schedule_cmds = re.findall(self.schedule_pattern, text)

        clean_text = re.sub(self.fg_pattern, "", text)
        clean_text = re.sub(self.bg_pattern, "", clean_text).strip()
        clean_text = re.sub(self.schedule_pattern,"",clean_text).strip()

        command = []
        for cmd in fg_cmds:
            command.append({
                "cmd": cmd.strip(),
                "mode": "foreground"
            })
        for cmd in bg_cmds:
            command.append({
                "cmd": cmd.strip(),
                "mode": "background"
            })
        for schedule in schedule_cmds:
            command.append({
                "cmd": schedule.strip(),
                "mode": "schedule"
            })

        return clean_text, command

    def filter_commands(self, command: str) -> bool:
        if not command:
            return False
        first_word = command.strip().split()[0].lower()
        return first_word not in self.denied_command

    def execute_commands(self, cmd_obj: dict) -> str:
        command = cmd_obj["cmd"]
        mode = cmd_obj.get("mode", "foreground")

        if mode == "schedule":
            return self._schedule(command)

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

    def _run_foreground(self, command: str) -> str:
        timeout = self._get_timeout(command)

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

    @staticmethod
    def _get_timeout(command: str) -> int:
        first_word = command.strip().split()[0].lower()

        timeouts = {
            'pacman': 600,
            'yay': 600,
            'paru': 600,
            'docker': 600,
            'git': 300,
        }

        return timeouts.get(first_word, 60)

    def _schedule(self, command: str):
        try:
            json_data = json.loads(command)
            data = json_data['data']

            run_at = datetime.fromisoformat(data['run_at'])
            message = data['message']
            repeat = data.get('repeat')

            self.scheduler.add(run_at, message, repeat)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            log.error(f"Invalid schedule: {e}")
            return f"Invalid schedule: {e}"