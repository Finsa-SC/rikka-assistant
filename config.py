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

    api_key: str|None = None

with get_config_path().open('rb') as f:
    conf = tomllib.load(f)

model_conf = conf['model']
monitor_conf = conf['monitor']
email_conf = conf['email']
model_memory_conf = conf['model']['memory']

config = AIConfig(
    provider=model_conf.get('provider'),
    model=model_conf.get('model'),
    voice_actor=model_conf.get('voice_actor'),

    monitor_enabled=monitor_conf.get('enabled'),
    monitor_interval=monitor_conf.get('interval'),

    email_host=email_conf.get('email_host'),
    email_port=email_conf.get('email_port'),
    email_user=email_conf.get('email_user'),
    email_password=email_conf.get('email_password'),

    memory_enabled=model_memory_conf.get('enabled'),
    max_message=model_memory_conf.get('max_message'),

    api_key=model_conf.get('api_key')
)