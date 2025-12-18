import json
import os

CONFIG_DIR = "data"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    # Prefer data/config.json, fallback to root config.json once
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Config file '{CONFIG_FILE}' is corrupted (invalid JSON): {e}")
            print("Please fix the config file or delete it to create a new one.")
            return None
        except Exception as e:
            print(f"Error reading config file '{CONFIG_FILE}': {e}")
            return None
    elif os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # migrate on next save
        except json.JSONDecodeError as e:
            print(f"Error: Config file 'config.json' is corrupted (invalid JSON): {e}")
            print("Please fix the config file or delete it to create a new one.")
            return None
        except Exception as e:
            print(f"Error reading config file 'config.json': {e}")
            return None
    else:
        return None
    # Strip deprecated pacing keys
    cfg.pop("min_send_interval", None)
    cfg.pop("max_flood_wait", None)
    return cfg

def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            filtered = {k: v for k, v in cfg.items() if k not in {"min_send_interval", "max_flood_wait"}}
            json.dump(filtered, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config file '{CONFIG_FILE}': {e}")
        raise
