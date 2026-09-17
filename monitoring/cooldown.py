from datetime import datetime, timedelta

class MonitorScheduler:
    def __init__(self):
        self.last_run = {}

    def should_run(self, rule: str, cooldown: int):
        last_run = self.last_run.get(rule, None)
        now = datetime.now()

        if last_run is None:
            self.last_run[rule] = now
            return True

        if now - last_run >= timedelta(seconds=cooldown):
            self.last_run[rule] = now
            return True

        return False