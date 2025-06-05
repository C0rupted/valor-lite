import os
import json
from typing import Any

SETTINGS_DIR = "settings"

SETTINGS_SCHEMA_TYPES_EXAMPLES = {
    "mod_roles": {
        "type": "list",
        "default": [],
        "description": "List of moderator role IDs."
    },
    "auto_moderation": {
        "type": "bool",
        "default": False,
        "description": "Enable or disable auto moderation."
    },
    "log_level": {
        "type": "value",
        "default": "info",
        "options": ["debug", "info", "warning", "error"],
        "description": "Logging verbosity level."
    },
    "welcome_message": {
        "type": "string",
        "default": "Welcome to the server!",
        "description": "Message to display when a user joins."
    }
}

SETTINGS_SCHEMA = {
    "guild_name": {
        "type": "string",
        "default": "",
        "description": "Name of the guild that this server belongs to"
    },
    "guild_tag": {
        "type": "string",
        "default": "",
        "description": "Tag of the guild that this server belongs to"
    }
}


class SettingsManager:
    def __init__(self, settings_dir: str = SETTINGS_DIR):
        self.settings_dir = settings_dir
        self.schema = SETTINGS_SCHEMA
        os.makedirs(self.settings_dir, exist_ok=True)

    def _get_file_path(self, server_id: int) -> str:
        return os.path.join(self.settings_dir, f"{server_id}.json")

    def _validate_key(self, key: str):
        if key not in self.schema:
            raise KeyError(f"Invalid setting: {key}")

    def _load(self, server_id: int) -> dict:
        path = self._get_file_path(server_id)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, server_id: int, data: dict):
        path = self._get_file_path(server_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _serialize(self, key: str, value: Any) -> Any:
        typ = self.schema[key]["type"]
        if typ == "list":
            if not isinstance(value, list):
                raise ValueError("Expected a list")
            return value
        elif typ == "bool":
            return bool(value)
        elif typ == "value":
            options = self.schema[key]["options"]
            if value not in options:
                raise ValueError(f"Invalid value for {key}: {value}")
            return value
        elif typ == "string":
            if not isinstance(value, str):
                raise ValueError("Expected a string")
            return value
        else:
            raise TypeError(f"Unsupported type: {typ}")

    def get(self, server_id: int, key: str) -> Any:
        self._validate_key(key)
        data = self._load(server_id)
        return data.get(key, self.schema[key]["default"])

    def set(self, server_id: int, key: str, value: Any):
        self._validate_key(key)
        data = self._load(server_id)
        serialized = self._serialize(key, value)
        data[key] = serialized
        self._save(server_id, data)