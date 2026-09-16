from monitoring.battery import battery_check
from monitoring.ram import insufficient_ram
from monitoring.cpu import cpu_pressure

def do_monitoring():
    issues = dict(type='system_event')

    ram = insufficient_ram()
    if ram:
        issues.update(ram=ram)

    cpu = cpu_pressure()
    if cpu:
        issues.update(cpu=cpu)

    battery = battery_check()
    if battery:
        issues.update(battery=battery)