import psutil

def battery_check():
    bat = psutil.sensors_battery()
    bat_percent = bat.percent
    bat_plugged = bat.power_plugged

    if bat_percent < 10 or bat_percent >= 100 and bat_plugged:
        return {
            'event': 'battery_value',
            'severity': 'warning',
            'data': {
                'battery_percent': bat_percent,
                'is_plugged': bat_plugged
            }
        }
    return None