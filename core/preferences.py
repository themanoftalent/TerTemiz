"""Persist UI preferences separately from the application installation."""
import json
import os
from pathlib import Path

DEFAULTS = {"theme": "system", "language": "tr"}

def preference_path():
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / ".config")) / "TerTemiz" / "preferences.json"

def load_preferences(path=None):
    try:
        data = json.loads(Path(path or preference_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    return {key: data.get(key) if data.get(key) in allowed else DEFAULTS[key]
            for key, allowed in {"theme": ("light", "dark", "system"), "language": ("tr", "en")}.items()}

def save_preferences(preferences, path=None):
    target = Path(path or preference_path())
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(preferences, ensure_ascii=False), encoding="utf-8")
    temporary.replace(target)
