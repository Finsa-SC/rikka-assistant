from monitoring.battery import battery_check
from monitoring.ram import insufficient_ram
from monitoring.cpu import cpu_pressure

def monitor():
    issues = dict(type='system_event')

    ram = insufficient_ram()
    if ram:
        issues['ram'] = ram

    cpu = cpu_pressure()
    if cpu:
        issues['cpu'] = cpu

    battery = battery_check()
    if battery:
        issues['battery'] = battery

    return issues if len(issues) > 1 else None