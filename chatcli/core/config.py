import yaml
from pathlib import Path

CONFIG_PATH = Path("config.yaml")

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("Missing config.yaml")
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)