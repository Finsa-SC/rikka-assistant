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

    # Memory
    memory_enabled: bool = False
    max_message: int     = 10

    api_key: str|None = None

with get_config_path().open('rb') as f:
    conf = tomllib.load(f)

model_conf = conf['model']
model_memory_conf = conf['model']['memory']
email_conf = conf['email']

config = AIConfig(
    provider=model_conf.get('provider'),
    model=model_conf.get('model'),
    voice_actor=model_conf.get('voice_actor'),

    email_host=email_conf.get('email_host'),
    email_port=email_conf.get('email_port'),
    email_user=email_conf.get('email_user'),
    email_password=email_conf.get('email_password'),

    memory_enabled=model_memory_conf.get('enabled'),
    max_message=model_memory_conf.get('max_message'),

    api_key=model_conf.get('api_key')
)