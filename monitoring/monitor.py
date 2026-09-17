from monitoring.rules import (
    battery_check, late_night, long_uptime,
    insufficient_ram, cpu_pressure
)
from .cooldown import MonitorScheduler

def monitor():
    scheduler = MonitorScheduler()

    issues = dict(type='system_event')

    ram = insufficient_ram()
    if ram and scheduler.should_run('ram', 180):
        issues['ram'] = ram

    cpu = cpu_pressure()
    if cpu and scheduler.should_run('cpu', 120):
        issues['cpu'] = cpu

    if battery := battery_check():
        issues['battery'] = battery

    if late_night() and scheduler.should_run('late_night', 86400):
        issues['late_night'] = late_night()

    if long_uptime() and scheduler.should_run('long_uptime', 21600):
        issues['long_uptime'] = long_uptime()

    return issues if len(issues) > 1 else None