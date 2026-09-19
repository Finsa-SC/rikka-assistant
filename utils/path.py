from pathlib import Path

def resolve_parent_path():
    parent_path = Path(__file__).resolve().parents[1]
    return parent_path

def get_config_path():
    parent_path = resolve_parent_path()
    return parent_path / "config.toml"