from psutil import virtual_memory

def insufficient_ram():
    ram = virtual_memory()
    if ram.free < 1_500_000_000:
        return {
            'event': 'memory_pleasure',
            'severety': 'urgent',
            'data': {
                'used': ram.used,
                'available': ram.available,
                'used_percent': ram.percent,
                'total': ram.total
            }
        }

    return None