import os
from pathlib import Path

import yaml

_SETTINGS_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.yaml"


def load_settings() -> dict:
    with open(_SETTINGS_PATH) as f:
        settings = yaml.safe_load(f)
    for key in settings:
        override = os.environ.get(key.upper())
        if override is not None:
            settings[key] = type(settings[key])(override)
    return settings
