import asyncio
from config_manager import load_config, save_config
from core import Forwarder

def _ask_list(prompt, is_numeric=False):
    while True:
        s = input(prompt).strip()
        if not s:
            return []
        items = [x.strip() for x in s.split(",") if x.strip()]
        
        if is_numeric:
            valid = True
            for item in items:
                try:
                    int(item)
                except ValueError:
                    print(f"Invalid input: '{item}' is not a number. Please enter numeric IDs.")
                    valid = False
                    break
            if valid:
                return items
        else:
            return items

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
    
    sources = _ask_list("Source channels (comma separated IDs): ", is_numeric=True)
    destinations = _ask_list("Destination channels (comma separated IDs): ", is_numeric=True)
    keywords = _ask_list("Keywords (comma separated): ")
    
    remove_signature = input("Remove signature? (y/n): ").lower() == "y"
    show_forward_tag = input("Show 'Forwarded from' tag in Telegram? (y/n): ").lower() == "y"
    signature_delimiters = _ask_list("Signature delimiters (comma separated, leave empty for none): ")

    print("Date format: YYYY-MM-DD (leave empty to skip)")
    start_date = input("Start Date: ").strip()
    end_date = input("End Date: ").strip()

    resume_from_last = input("Resume from last forwarded message? (y/n): ").lower() == "y"
    highlight_keywords = input("Highlight keywords in message? (y/n): ").lower() == "y"

    scan_old = input("Scan old messages? (y/n): ").lower() == "y"
    raw_limit = input("Old scan limit (leave empty for ALL): ").strip()
    if raw_limit == "":
        limit_messages = None
        scan_all = True
    else:
        try:
            limit_messages = int(raw_limit)
            if limit_messages < 0:
                print("Invalid limit. Negative numbers are not allowed. Using 0 (ALL)")
                limit_messages = None
                scan_all = True
            else:
                scan_all = False
        except ValueError:
            print("Invalid number. Using 0 (ALL)")
            limit_messages = None
            scan_all = True

    while True:
        session_name = input("Session name: ").strip()
        if session_name:
            break
        print("Session name cannot be empty. Please enter a valid session name.")
    
    mode = input("Mode (past/live/both): ").lower().strip()
    if mode not in ("past", "live", "both"):
        while mode not in ("past", "live", "both"):
            mode = input("Invalid mode. Enter one of past/live/both: ").lower().strip()

    cfg = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
        "sources": sources,
        "destinations": destinations,
        "keywords": keywords,
        "remove_signature": remove_signature,
        "signature_delimiters": signature_delimiters,
        "limit_messages": limit_messages,
        "session_name": session_name,
        "mode": mode,
        "scan_old": scan_old,
        "scan_all": scan_all,
        "show_forward_tag": show_forward_tag,
        "start_date": start_date,
        "end_date": end_date,
        "resume_from_last": resume_from_last,
        "highlight_keywords": highlight_keywords
    }

    save_config(cfg)
    return cfg

async def start_loop():
    cfg = load_config()
    if cfg is None:
        cfg = request_config()
    else:
        if "highlight_keywords" not in cfg and "bold_keywords" in cfg:
            cfg["highlight_keywords"] = bool(cfg.get("bold_keywords", False))
            cfg.pop("bold_keywords", None)

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
