import asyncio
from telethon import TelegramClient, events
from colorama import Fore, init
from utils import match_keywords, strip_signature


init(autoreset=True)

class Forwarder:
    def __init__(self, cfg):
        self.cfg = cfg
        
        required_fields = ["session_name", "api_id", "api_hash", "phone", "sources", "destinations"]
        for field in required_fields:
            if field not in cfg:
                raise ValueError(f"Missing required configuration field: '{field}'")
        
        if not isinstance(cfg["api_id"], int):
            raise ValueError("api_id must be an integer")
        
        if not isinstance(cfg["api_hash"], str) or not cfg["api_hash"]:
            raise ValueError("api_hash must be a non-empty string")
        
        if not isinstance(cfg["phone"], str) or not cfg["phone"]:
            raise ValueError("phone must be a non-empty string")
        
        if not isinstance(cfg["session_name"], str) or not cfg["session_name"]:
            raise ValueError("session_name must be a non-empty string")
        
        self.client = TelegramClient(cfg["session_name"], cfg["api_id"], cfg["api_hash"])
        
        if not isinstance(cfg["sources"], list):
            raise ValueError("sources must be a list")
        if not isinstance(cfg["destinations"], list):
            raise ValueError("destinations must be a list")
        
        try:
            self.sources = [int(x) for x in cfg["sources"]]
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid source channel IDs: {e}. All source IDs must be numeric.")
        
        try:
            self.destinations = [int(x) for x in cfg["destinations"]]
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid destination channel IDs: {e}. All destination IDs must be numeric.")
        
        keywords = cfg.get("keywords", [])
        if not isinstance(keywords, list):
            raise ValueError("keywords must be a list")
        self.keywords = keywords
        
        self.remove_signature = cfg.get("remove_signature", False)
        
        signature_delimiters = cfg.get("signature_delimiters", [])
        if not isinstance(signature_delimiters, list):
            raise ValueError("signature_delimiters must be a list")
        self.signature_delimiters = signature_delimiters
        self.limit_messages = cfg.get("limit_messages", None)
        if self.limit_messages is not None and self.limit_messages < 0:
            print(Fore.YELLOW + f"Invalid limit_messages ({self.limit_messages}). Negative values are not allowed. Setting to None (scan all).")
            self.limit_messages = None
            self.scan_all = True
        else:
            self.scan_all = cfg.get("scan_all", False)
        self.mode = cfg.get("mode", "both")
        self.show_forward_tag = cfg.get("show_forward_tag", True)
        
        if not self.sources:
            raise ValueError("At least one source channel is required")
        if not self.destinations:
            raise ValueError("At least one destination channel is required")
        if self.mode not in ("post", "live", "both"):
            print(Fore.YELLOW + f"Invalid mode '{self.mode}', defaulting to 'both'")
            self.mode = "both"

    async def start(self):
        await self.client.start(self.cfg["phone"])

    async def _process_and_send(self, dest, msg):
        if self.show_forward_tag:
            await msg.forward_to(dest)
            return "Forwarded"
        else:
            text = msg.text or ""
            if self.remove_signature and text:
                text = strip_signature(text, self.signature_delimiters)
            
            if msg.media:
                await self.client.send_file(dest, msg.media, caption=text if text else None)
            else:
                if text:
                    await self.client.send_message(dest, text)
                else:
                    await msg.forward_to(dest)
            return "Copied"

    async def forward_old_messages(self):
        count = 0
        for src in self.sources:
            try:
                if self.scan_all or (self.limit_messages is None) or (self.limit_messages == 0):
                    limit = None
                    print(Fore.YELLOW + f"Scanning ALL messages from source {src} (Old -> New) ...")
                else:
                    limit = self.limit_messages
                    print(Fore.YELLOW + f"Scanning last {limit} messages from source {src} (Old -> New) ...")

                messages = await self.client.get_messages(src, limit=limit)
                if not messages:
                    print(Fore.YELLOW + f"No messages found in source {src}")
                    continue
                    
                for msg in reversed(messages):
                    text = msg.text or ""
                    if match_keywords(text, self.keywords):
                        for d in self.destinations:
                            try:
                                action = await self._process_and_send(d, msg)
                                print(Fore.GREEN + f"{action} message from {src} -> {d}")
                                count += 1
                            except Exception as e:
                                print(Fore.RED + f"Failed to process from {src} to {d}: {e}")
            except Exception as e:
                print(Fore.RED + f"Error accessing source {src}: {e}")
                            
        print(Fore.CYAN + f"Processed old messages: {count}")

    def register_handlers(self):
        @self.client.on(events.NewMessage(chats=self.sources))
        async def handler(event):
            text = event.message.text or ""
            
            if self.mode == "post":
                if match_keywords(text, self.keywords):
                    for d in self.destinations:
                        try:
                            action = await self._process_and_send(d, event.message)
                            print(Fore.GREEN + f"{action} live (post-mode) from {event.chat_id} -> {d}")
                        except Exception as e:
                            print(Fore.RED + f"Error processing live (post-mode) to {d}: {e}")
            
            elif self.mode == "live":
                for d in self.destinations:
                    try:
                        action = await self._process_and_send(d, event.message)
                        print(Fore.GREEN + f"{action} live (live-mode) from {event.chat_id} -> {d}")
                    except Exception as e:
                        print(Fore.RED + f"Error processing live (live-mode) to {d}: {e}")
            
            elif self.mode == "both":
                for d in self.destinations:
                    try:
                        action = await self._process_and_send(d, event.message)
                        print(Fore.GREEN + f"{action} live (both-mode) from {event.chat_id} -> {d}")
                    except Exception as e:
                        print(Fore.RED + f"Error processing live (both-mode) to {d}: {e}")

    async def run(self):
        if self.cfg.get("scan_old", False) and (self.mode in ("post", "both")):
            await self.forward_old_messages()
            if self.mode == "both":
                print(Fore.CYAN + "Mode is 'both': Old message scanning completed. Now forwarding new messages live.")
        elif self.mode == "live":
            print(Fore.YELLOW + "Mode is 'live': Old message scanning is paused. Only forwarding new messages.")
        self.register_handlers()
        await self.client.run_until_disconnected()
