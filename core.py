import asyncio
import os
from datetime import datetime, timezone
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import FloodWaitError, SlowModeWaitError, ChatWriteForbiddenError, UserBannedInChannelError, PeerFloodError, ChannelPrivateError, ChannelInvalidError, ChatAdminRequiredError
from telethon.errors import FloodWaitError as FloodWaitErrorAlt, SlowModeWaitError as SlowModeWaitErrorAlt
from telethon.tl.types import MessageMediaWebPage
from colorama import Fore, init
from utils import match_keywords, strip_signature, highlight_keywords, escape_html
from state_manager import get_last_read_message_id, update_last_read_message_id

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
        
        sname = cfg["session_name"]
        if not os.path.isabs(sname) and not os.path.dirname(sname):
            sname = os.path.join("data", sname)
        dirn = os.path.dirname(sname)
        if dirn:
            os.makedirs(dirn, exist_ok=True)
        self.client = TelegramClient(sname, cfg["api_id"], cfg["api_hash"])
        self.client.parse_mode = 'html'
        
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
        self.resume_from_last = cfg.get("resume_from_last", False)
        self.highlight_keywords = cfg.get("highlight_keywords", cfg.get("bold_keywords", False))
        self.append_timestamp_footer = bool(cfg.get("append_timestamp_footer", False))
        self.id_min = cfg.get("id_min", None)
        self.id_max = cfg.get("id_max", None)
        self._dest_locks = {}
        self.min_send_interval = 0.0
        self._global_send_lock = asyncio.Lock()
        self._last_send_ts = 0.0
        self.max_flood_wait = None
        self.caption_limit = 1024
        
        if not self.sources:
            raise ValueError("At least one source channel is required")
        if not self.destinations:
            raise ValueError("At least one destination channel is required")
        if self.mode not in ("past", "live", "both", "id_range"):
            print(Fore.YELLOW + f"Invalid mode '{self.mode}', defaulting to 'both'")
            self.mode = "both"
        try:
            if self.id_min is not None:
                self.id_min = int(self.id_min)
        except Exception:
            print(Fore.RED + "Invalid id_min. Ignoring.")
            self.id_min = None
        try:
            if self.id_max is not None:
                self.id_max = int(self.id_max)
        except Exception:
            print(Fore.RED + "Invalid id_max. Ignoring.")
            self.id_max = None
        if self.mode == "id_range" and (self.id_min is None or self.id_max is None or self.id_min > self.id_max):
            print(Fore.RED + "Invalid id_range configuration. Please set id_min <= id_max.")
            self.mode = "both"

        self.start_date = None
        if cfg.get("start_date"):
            try:
                self.start_date = datetime.strptime(cfg["start_date"], "%Y-%m-%d").date()
            except ValueError:
                print(Fore.RED + f"Invalid start_date format ({cfg['start_date']}). Ignoring date filter.")

        self.end_date = None
        if cfg.get("end_date"):
            try:
                self.end_date = datetime.strptime(cfg["end_date"], "%Y-%m-%d").date()
            except ValueError:
                print(Fore.RED + f"Invalid end_date format ({cfg['end_date']}). Ignoring date filter.")

    async def start(self):
        await self.client.start(self.cfg["phone"])

    def _get_lock(self, dest):
        lock = self._dest_locks.get(dest)
        if lock is None:
            lock = asyncio.Lock()
            self._dest_locks[dest] = lock
        return lock

    async def _with_retry(self, fn):
        while True:
            try:
                async with self._global_send_lock:
                    if self.min_send_interval > 0:
                        now = asyncio.get_running_loop().time()
                        if self._last_send_ts > 0:
                            delta = now - self._last_send_ts
                            if delta < self.min_send_interval:
                                await asyncio.sleep(self.min_send_interval - delta)
                res = await fn()
                async with self._global_send_lock:
                    self._last_send_ts = asyncio.get_running_loop().time()
                return res
            except (FloodWaitError, FloodWaitErrorAlt) as e:
                s = getattr(e, "seconds", 0)
                await asyncio.sleep(s + 1)
                continue
            except (SlowModeWaitError, SlowModeWaitErrorAlt) as e:
                s = getattr(e, "seconds", 0)
                await asyncio.sleep(s + 1)
                continue
            except (ChatWriteForbiddenError, UserBannedInChannelError) as e:
                raise e
            except (PeerFloodError,) as e:
                raise RuntimeError("Skip send due to peer flood")
            except (ChannelPrivateError, ChannelInvalidError, ChatAdminRequiredError) as e:
                raise e
            except Exception as e:
                raise e

    async def _process_and_send(self, dest, msg):
        lock = self._get_lock(dest)
        async with lock:
            if self.show_forward_tag:
                await self._with_retry(lambda: msg.forward_to(dest))
                return "Forwarded"
            else:
                text = msg.text or ""
                if self.remove_signature and text:
                    text = strip_signature(text, self.signature_delimiters)
                
                if text:
                    text = escape_html(text)
                    if self.highlight_keywords:
                        text = highlight_keywords(text, self.keywords)

                footer = ""
                if self.append_timestamp_footer:
                    orig = getattr(getattr(msg, "fwd_from", None), "date", None) or msg.date
                    if getattr(orig, "tzinfo", None) is None:
                        orig = orig.replace(tzinfo=timezone.utc)
                    dt_local = orig.astimezone()
                    footer = "\n\n" + f"{dt_local.strftime('%Y-%m-%d %H:%M')}"

                has_downloadable_media = bool(msg.media) and not isinstance(msg.media, MessageMediaWebPage)
                if has_downloadable_media:
                    cap = (text + footer) if footer else (text if text else None)
                    if cap and len(cap) > self.caption_limit:
                        await self._with_retry(lambda: self.client.send_file(dest, msg.media))
                        await self._with_retry(lambda: self.client.send_message(dest, cap))
                    else:
                        await self._with_retry(lambda: self.client.send_file(dest, msg.media, caption=cap))
                    return "Copied"
                if text:
                    final_text = text
                    wp = getattr(msg.media, "webpage", None)
                    url = getattr(wp, "url", None) if wp else None
                    if url and (url not in final_text):
                        final_text = f"{final_text}\n{url}" if final_text else url
                    if footer:
                        final_text = f"{final_text}{footer}"
                    await self._with_retry(lambda: self.client.send_message(dest, final_text))
                    return "Copied"
                await self._with_retry(lambda: msg.forward_to(dest))
                return "Forwarded (fallback)"

    async def forward_id_range(self):
        count = 0
        for src in self.sources:
            try:
                min_id = (self.id_min - 1) if self.id_min is not None else None
                max_id = (self.id_max + 1) if self.id_max is not None else None
                had_any = False
                async for msg in self.client.iter_messages(src, reverse=True, min_id=min_id, max_id=max_id):
                    had_any = True
                    for d in self.destinations:
                        try:
                            action = await self._process_and_send(d, msg)
                            print(Fore.GREEN + f"{action} message from {src} -> {d}")
                            count += 1
                        except Exception as e:
                            print(Fore.RED + f"Failed to process from {src} to {d}: {e}")
                    update_last_read_message_id(src, msg.id)
                if not had_any:
                    print(Fore.YELLOW + f"No messages in range for source {src}")
            except Exception as e:
                print(Fore.RED + f"Error accessing source {src}: {e}")
        print(Fore.CYAN + f"Processed id range messages: {count}")

    async def forward_old_messages(self):
        count = 0
        for src in self.sources:
            try:
                min_id = 0
                if self.resume_from_last:
                    print(Fore.CYAN + f"Checking history for source {src}...")
                    min_id = get_last_read_message_id(src)
                    if min_id > 0:
                        print(Fore.GREEN + f"Found last processed message ID: {min_id}. Resuming from there.")
                    else:
                        print(Fore.YELLOW + "No history found in state file. Scanning from beginning (or based on limit).")

                use_window = (self.start_date is not None and self.end_date is not None)
                if use_window:
                    print(Fore.YELLOW + f"Scanning source {src} within {self.start_date} to {self.end_date}...")
                    offset_dt = datetime(self.start_date.year, self.start_date.month, self.start_date.day, tzinfo=timezone.utc)
                    async for msg in self.client.iter_messages(src, reverse=True, offset_date=offset_dt):
                        d = msg.date.date()
                        if d < self.start_date:
                            continue
                        if d > self.end_date:
                            break

                        text = msg.text or ""
                        if match_keywords(text, self.keywords):
                            for dch in self.destinations:
                                try:
                                    action = await self._process_and_send(dch, msg)
                                    print(Fore.GREEN + f"{action} message from {src} -> {dch}")
                                    count += 1
                                except Exception as e:
                                    print(Fore.RED + f"Failed to process from {src} to {dch}: {e}")
                        update_last_read_message_id(src, msg.id)
                    continue
                limit = self.limit_messages
                if self.scan_all or (limit is None) or (limit == 0):
                    limit = None
                if min_id > 0:
                    print(Fore.YELLOW + f"Scanning source {src} starting after ID {min_id} (Limit: {limit if limit else 'All'})...")
                else:
                    print(Fore.YELLOW + f"Scanning source {src} (Limit: {limit if limit else 'All'})...")
                processed = 0
                had_any = False
                async for msg in self.client.iter_messages(src, reverse=True, min_id=min_id):
                    had_any = True
                    if self.start_date and msg.date.date() < self.start_date:
                        continue
                    if self.end_date and msg.date.date() > self.end_date:
                        continue

                    text = msg.text or ""
                    if match_keywords(text, self.keywords):
                        for d in self.destinations:
                            try:
                                action = await self._process_and_send(d, msg)
                                print(Fore.GREEN + f"{action} message from {src} -> {d}")
                                count += 1
                            except Exception as e:
                                print(Fore.RED + f"Failed to process from {src} to {d}: {e}")

                    update_last_read_message_id(src, msg.id)
                    if limit is not None:
                        processed += 1
                        if processed >= limit:
                            break
                if not had_any:
                    print(Fore.YELLOW + f"No new messages found in source {src}")

            except Exception as e:
                print(Fore.RED + f"Error accessing source {src}: {e}")
                            
        print(Fore.CYAN + f"Processed old messages: {count}")

    def register_handlers(self):
        @self.client.on(events.NewMessage(chats=self.sources))
        async def handler(event):
            msg = event.message
            text = msg.text or ""
            src_id = event.chat_id
            
            should_forward = False
            within_date = True
            if self.start_date and msg.date.date() < self.start_date:
                within_date = False
            if self.end_date and msg.date.date() > self.end_date:
                within_date = False
            
            if self.mode == "live":
                if match_keywords(text, self.keywords):
                    should_forward = True
            elif self.mode in ("past", "both"):
                if match_keywords(text, self.keywords):
                    should_forward = True
            
            if should_forward and within_date:
                for d in self.destinations:
                    try:
                        action = await self._process_and_send(d, msg)
                        print(Fore.GREEN + f"{action} live from {src_id} -> {d}")
                    except Exception as e:
                        print(Fore.RED + f"Error processing live to {d}: {e}")
            
            update_last_read_message_id(src_id, msg.id)

    async def run(self):
        if self.mode == "past":
            if self.cfg.get("scan_old", False):
                await self.forward_old_messages()
                print(Fore.CYAN + "Mode is 'past': Old message scanning completed. Exiting.")
            else:
                print(Fore.YELLOW + "Mode is 'past' with old scanning disabled: Nothing to do. Exiting.")
            await self.client.disconnect()
            return
        if self.cfg.get("scan_old", False) and self.mode == "both":
            await self.forward_old_messages()
            print(Fore.CYAN + "Mode is 'both': Old message scanning completed. Now forwarding new messages live.")
        elif self.mode == "live":
            print(Fore.YELLOW + "Mode is 'live': Old message scanning is paused. Only forwarding new messages.")
        elif self.mode == "id_range":
            await self.forward_id_range()
            await self.client.disconnect()
            return
        self.register_handlers()
        print(Fore.GREEN + "Listening for new messages...")
        await self.client.run_until_disconnected()
