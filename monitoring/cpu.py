import psutil

def cpu_pressure():
    usage = psutil.cpu_percent(interval=None)
    temps = psutil.sensors_temperatures()
    cpu_temp = temps['k10temp'][0].current

    if _drop_cpu(usage, cpu_temp):
        return {
            'event': 'cpu_pressure',
            'severity': 'warning',
            'data': {
                'usage_percent': usage,
                'temperature_c': cpu_temp
            }
        }
    return None

def _drop_cpu(usage: float, cpu_temp):
    if usage > 90.0:
        return True

    if cpu_temp > 90:
        return True

    return False