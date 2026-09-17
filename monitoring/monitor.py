from logger import get_logger
from monitoring.rules import (
    battery_check, late_night, long_uptime,
    insufficient_ram, cpu_pressure
)
from .cooldown import MonitorScheduler
import subprocess, json

logger = get_logger("Monitor")

scheduler = MonitorScheduler()
def polling_monitor():
    issues = dict(type="system_event")

    ram = insufficient_ram()
    if ram and scheduler.should_run("ram", 180):
        logger.warning(f"RAM issue detected: {ram}")
        issues["ram"] = ram

    cpu = cpu_pressure()
    if cpu and scheduler.should_run("cpu", 120):
        logger.warning(f"CPU issue detected: {cpu}")
        issues["cpu"] = cpu

    if battery := battery_check():
        logger.warning(f"Battery issue detected: {battery}")
        issues["battery"] = battery

    if late := late_night():
        if scheduler.should_run("late_night", 86400):
            logger.info("Late night event detected")
            issues["late_night"] = late

    if uptime := long_uptime():
        if scheduler.should_run("long_uptime", 21600):
            logger.info("Long uptime event detected")
            issues["long_uptime"] = uptime

    if len(issues) >= 1:
        logger.warning(f"Polling generated system event: {issues}")
        return issues
    return None

def event_watcher(callback):
    process = subprocess.Popen(
        ['journalctl', '-f', '-p', 'err', '-o', 'json'],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    for line in process.stdout:
        entry = json.loads(line)

        logger.warning(f"System error detected: {entry.get('MESSAGE')}")
        callback(entry)