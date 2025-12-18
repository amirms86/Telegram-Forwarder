import json
import os

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "forwarder_state.json")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state file: {e}")
            return {}
    if os.path.exists("forwarder_state.json"):
        try:
            with open("forwarder_state.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state file: {e}")
            return {}
    return {}

def save_state(state):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"Error saving state file: {e}")
        
def get_last_read_message_id(source_id):
    state = load_state()
    return state.get(str(source_id), 0)

def update_last_read_message_id(source_id, message_id):
    state = load_state()
    current_id = state.get(str(source_id), 0)
    if message_id > current_id:
        state[str(source_id)] = message_id
        save_state(state)
