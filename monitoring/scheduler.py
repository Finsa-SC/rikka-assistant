import json, string, random
import time
from datetime import datetime

from logger import get_logger
from monitoring.event_queue import event_queue
from utils.path import resolve_parent_path

logger = get_logger('Scheduler')

class Scheduler:
    def __init__(self):
        self.schedules = []
        self.schedule_path = resolve_parent_path() / "data" / "schedules.json"

    def add(self, run_at: datetime, message: str, repeat: int|None=None):
        schedule_id = (
            ''.join(random.choices(string.hexdigits, k=6))
        )
        self.schedules.append(
            {
                'id': schedule_id,
                'data': {
                    'run_at': run_at,
                    'message': message,
                    'repeat': repeat
                }
            }
        )
        self.write()

    def remove(self, schedule_id: str):
        for schedule in self.schedules:
            if schedule['id'] == schedule_id:
                self.schedules.remove(schedule)
        self.write()

    def load(self):
        with self.schedule_path.open('r') as f:
            self.schedules = json.load(f)

    def write(self):
        with self.schedule_path.open('w') as f:
            json.dump(
                self.schedules,
                f,
                indent=4,
                default=lambda obj: obj.isoformat()
            )
        self.load()

    def run(self):
        self.load()

        while True:
            now = datetime.now().astimezone()

            for schedule in self.schedules:
                schedule_id = schedule['id']
                schedule_data = schedule['data']
                run_at = datetime.fromisoformat(schedule_data['run_at'])
                message = schedule_data['message']
                repeat = schedule_data['repeat']

                if now >= run_at:
                    event = {
                        'type': 'times up',
                        'severity': 'info',
                        'data': {
                            'run_at': run_at,
                            'message': message,
                            'repeat': repeat,
                        }
                    }

                    logger.info(f"Schedule trigger for {schedule_id}")

                    event_queue.put(
                        f"[SYSTEM_SCHEDULE]\n"
                        f"reminder: {event}"
                    )
                    self.remove(schedule_id)

            time.sleep(60)

scheduler = Scheduler()