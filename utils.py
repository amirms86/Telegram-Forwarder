def match_keywords(text, keywords):
    if not text:
        return False
    if not keywords:
        return True
    return any(k in text for k in keywords)

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
