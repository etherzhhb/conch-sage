import os
import yaml
from pathlib import Path

def load_config():
    config_path = Path(os.environ.get("CONCH_CONFIG", "config.yaml"))

    if not config_path.exists():
        raise FileNotFoundError(f"Missing config file: {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)
