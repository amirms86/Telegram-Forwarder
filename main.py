import asyncio
from config_manager import load_config, save_config
from core import Forwarder

def _ask_list(prompt):
    s = input(prompt).strip()
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]

def request_config():
    while True:
        try:
            api_id = int(input("API ID: "))
            break
        except ValueError:
            print("Invalid API ID. Please enter a number.")
    while True:
        api_hash = input("API HASH: ").strip()
        if api_hash:
            break
        print("API HASH cannot be empty. Please enter a valid API HASH.")
    
    while True:
        phone = input("Phone (+98...): ").strip().replace(" ", "")
        if phone:
            break
        print("Phone number cannot be empty. Please enter a valid phone number.")
    
    sources = _ask_list("Source channels (comma separated): ")
    destinations = _ask_list("Destination channels (comma separated): ")
    keywords = _ask_list("Keywords (comma separated): ")
    remove_signature = input("Remove signature? (y/n): ").lower() == "y"
    
    show_forward_tag = input("Show 'Forwarded from' tag in Telegram? (y/n): ").lower() == "y"

    raw_limit = input("Old scan limit (enter 0 or leave empty to scan ALL): ").strip()
    if raw_limit == "" or raw_limit == "0":
        limit_messages = 0
        scan_all = True
    else:
        try:
            limit_messages = int(raw_limit)
            if limit_messages < 0:
                print("Invalid limit. Negative numbers are not allowed. Using default: 100")
                limit_messages = 100
            scan_all = False
        except ValueError:
            limit_messages = 100
            scan_all = False

    while True:
        session_name = input("Session name: ").strip()
        if session_name:
            break
        print("Session name cannot be empty. Please enter a valid session name.")
    
    mode = input("Mode (post/live/both): ").lower().strip()
    if mode not in ("post", "live", "both"):
        mode = "both"

    cfg = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
        "sources": sources,
        "destinations": destinations,
        "keywords": keywords,
        "remove_signature": remove_signature,
        "signature_delimiters": ["--", "—", "Regards:", "Thanks"],
        "limit_messages": limit_messages,
        "session_name": session_name,
        "mode": mode,
        "scan_old": True,
        "scan_all": scan_all,
        "show_forward_tag": show_forward_tag 
    }

    save_config(cfg)
    return cfg

async def start_loop():
    cfg = load_config()
    if cfg is None:
        cfg = request_config()
    
    if "show_forward_tag" not in cfg:
        print("New setting 'show_forward_tag' not found in config. Defaulting to True.")
        cfg["show_forward_tag"] = True

    try:
        fwd = Forwarder(cfg)
        await fwd.start()
        await fwd.run()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your config.json file or run the setup again.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(start_loop())
