import re
import html


def _clean_keywords(keywords):
    return [str(k).lower() for k in (keywords or []) if str(k).strip()]


def match_keywords(text, keywords):
    cleaned_keywords = _clean_keywords(keywords)
    if not cleaned_keywords:
        return True
    if not text:
        return False

    text_lower = text.lower()
    return any(k in text_lower for k in cleaned_keywords)


def should_forward_by_keywords(text, whitelist_keywords, blacklist_keywords=None):
    blacklist = _clean_keywords(blacklist_keywords)
    if blacklist and text:
        text_lower = text.lower()
        if any(k in text_lower for k in blacklist):
            return False
    return match_keywords(text, whitelist_keywords)


def escape_html(text):
    if not text:
        return text
    return html.escape(text)


def highlight_keywords(text, keywords):
    cleaned_keywords = _clean_keywords(keywords)
    if not text or not cleaned_keywords:
        return text
    sorted_keywords = sorted(cleaned_keywords, key=len, reverse=True)
    escaped_keywords = [re.escape(k) for k in sorted_keywords]
    pattern = re.compile("|".join(escaped_keywords), re.IGNORECASE)

    def replace(match):
        return f"<u><b><i>{match.group(0)}</i></b></u>"

    return pattern.sub(replace, text)


def strip_signature(text, delimiters):
    if not text:
        return text
    for d in delimiters:
        pos = text.rfind(d)
        if pos > -1:
            return text[:pos].strip()
    parts = text.strip().splitlines()
    if len(parts) > 1 and len(parts[-1]) < 40:
        return "\n".join(parts[:-1]).strip()
    return text


async def get_entity_name(client, entity):
    try:
        ent = await client.get_entity(entity)
    except Exception:
        try:
            return str(entity)
        except Exception:
            return "unknown"
    title = getattr(ent, "title", None)
    if title:
        return title
    uname = getattr(ent, "username", None)
    if uname:
        return f"@{uname}"
    first = getattr(ent, "first_name", None)
    last = getattr(ent, "last_name", None)
    if first or last:
        return " ".join([p for p in (first, last) if p])
    eid = getattr(ent, "id", None)
    if eid is not None:
        return f"id:{eid}"
    return "unknown"
