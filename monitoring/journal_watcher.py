import json, subprocess

from logger import get_logger
from monitoring.event_queue import event_queue

logger = get_logger("JournalWatcher")

def journal_watcher():
    process = subprocess.Popen(
        [
            'journalctl',
            '-f',
            '-n', '0',
            '-p', 'err',
            '-o', 'json'
        ],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    for line in process.stdout:
        entry = json.loads(line)

        logger.warning(f"System error detected: {entry.get('MESSAGE')}")

        error_message = {
            'type': 'journal_error',
            'severity': 'err',
            'message': entry.get('MESSAGE'),
            'source': {
                'identifier': entry.get('SYSLOG_IDENTIFIER'),
                'process': entry.get('_COMM'),
                'pid': entry.get('_PID'),
            }
        }

        event_queue.put(f"[SYSTEM_JOURNAL]\n{error_message}")