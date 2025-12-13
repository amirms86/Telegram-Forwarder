import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Config file '{CONFIG_FILE}' is corrupted (invalid JSON): {e}")
            print("Please fix the config file or delete it to create a new one.")
            return None
        except Exception as e:
            print(f"Error reading config file '{CONFIG_FILE}': {e}")
            return None
    return None

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config file '{CONFIG_FILE}': {e}")
        raise
