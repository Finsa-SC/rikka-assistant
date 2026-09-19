from time import time
from datetime import datetime
import psutil


def late_night():
    if datetime.now().hour >= 22:
        return {
            'event': "master_healthy",
            'severety': 'urgent',
            'data': {
                'time_now': datetime.now(),
                'description': "It's already late at night, remind the master to rest and threaten him to forcibly shut down the computer because the health of the body is more important"
            }
        }
    return None

def long_uptime():
    up_time = time() - psutil.boot_time()
    max_uptime = (5 * 60 * 60)

    if up_time > max_uptime:
        return {
            'event': "master_healthy",
            'severety': 'urgent',
            'data': {
                'computer_uptime': up_time,
                'description': "Master has been using the computer for a long time, remind him to immediately rest and turn off his computer, tell him to touch the grass and look at the sky"
            }
        }
    return None