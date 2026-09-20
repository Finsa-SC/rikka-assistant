import tomllib

from utils.path import get_config_path
from dataclasses import dataclass

@dataclass(frozen=True)
class AIConfig:
    # Model
    provider:   str
    model:      str

    voice_actor:str
    # Email
    email_user:     str
    email_password: str
    email_host:     str = "imap.gmail.com"

    email_port:     int = 993
    # Monitor
    monitor_enabled: bool = False

    monitor_interval: int = 60
    # Memory
    memory_enabled: bool = False

    max_message: int     = 10
    max_command_depth: int = 5
    api_key: str|None = None


with get_config_path().open('rb') as f:
    conf = tomllib.load(f)

model_conf = conf['model']
monitor_conf = conf['monitor']
email_conf = conf['email']
model_memory_conf = conf['model']['memory']

# Model
provider = model_conf.get('provider')
model = model_conf.get('model')
voice_actor = model_conf.get('voice_actor')
max_command_depth = model_conf.get('max_command_depth')
# Monitor
monitor_enabled = monitor_conf.get('enabled')
monitor_interval = monitor_conf.get('interval')
# Email
email_host = email_conf.get('email_host')
email_port = email_conf.get('email_port')
email_user = email_conf.get('email_user')
email_password = email_conf.get('email_password')
# Memory
memory_enabled = model_memory_conf.get('enabled', False)
max_message = model_memory_conf.get('max_message', 10)

def validate_config():
    if not provider and not model and not voice_actor and not email_user and not email_password:
        raise ValueError("Required field must be fill in config")

    if monitor_enabled:
        if not isinstance(monitor_interval, int) or (isinstance(monitor_interval, int) and monitor_interval < 0):
            raise ValueError("Invalid interval for monitor interval")

    if memory_enabled:
        if not isinstance(max_message, int) or (isinstance(max_message, int) and max_message < 0):
            raise ValueError("Invalid max message value")

    if not isinstance(max_command_depth, int) or (isinstance(max_command_depth, int) and max_command_depth < 0):
        raise ValueError("Invalid value for max command depth in config")

validate_config()

config = AIConfig(
    provider=provider,
    model=model,
    voice_actor=voice_actor,

    monitor_enabled=monitor_enabled,
    monitor_interval=monitor_interval,

    email_host=email_host,
    email_port=email_port,
    email_user=email_user,
    email_password=email_password,

    memory_enabled=memory_enabled,
    max_message=max_message,

    max_command_depth=max_command_depth,
    api_key=model_conf.get('api_key'),
)