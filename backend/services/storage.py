import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"


def read_settings():
    if not SETTINGS_FILE.exists():
        return {}

    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_settings(settings):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return settings
