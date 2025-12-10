import os
import json
import re
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from telethon.tl.types import PeerUser

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

def analyze_mentions(user_folder, top_n=20, save_path="web/static/mentions.png"):
    message_files = [f for f in os.listdir(user_folder) if f.startswith("messages_") and f.endswith(".json")]
    mention_counter = Counter()
    mention_pattern = re.compile(r"@[\w\d_]{4,}")
    for file in message_files:
        path = os.path.join(user_folder, file)
        with open(path, encoding="utf-8") as f:
            messages = json.load(f)
            for msg in messages:
                text = msg.get("text")
                if not isinstance(text, str):
                    continue
                mentions = mention_pattern.findall(text)
                mention_counter.update(mentions)
    out_path = os.path.join(user_folder, "mentions.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(mention_counter.most_common(), f, indent=4, ensure_ascii=False)

    top_mentions = mention_counter.most_common(top_n)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if not top_mentions:
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, "No mentions found", ha="center", va="center")
        plt.axis("off")
        plt.savefig(save_path, bbox_inches="tight")
        plt.close()
        return

    labels, counts = zip(*top_mentions)
    plt.figure(figsize=(10, max(3, 0.5 * len(labels) + 1)))
    plt.barh(range(len(labels)), counts)
    plt.yticks(range(len(labels)), labels)
    plt.xlabel("Count")
    plt.title("Top mentions")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()

def _load_user_map(user_folder):
    p = os.path.join(user_folder, "user_map.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_user_map(user_folder, mapping):
    p = os.path.join(user_folder, "user_map.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4, ensure_ascii=False)

async def _resolve_usernames_async(ids):
    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")
    session = os.getenv("TG_SESSION")
    if not api_id or not api_hash:
        return {}
    sess = StringSession(session) if session else "osint_session"
    async with TelegramClient(sess, int(api_id), api_hash) as client:
        res = {}
        for uid in ids:
            try:
                ent = await client.get_entity(int(uid))
                uname = getattr(ent, "username", None)
                if uname:
                    res[str(uid)] = f"@{uname}"
            except Exception:
                pass
        return res

def _resolve_usernames(user_folder, ids):
    cached = _load_user_map(user_folder)
    missing = {str(i) for i in ids if str(i) not in cached}
    found = {}
    if missing:
        try:
            found = asyncio.run(_resolve_usernames_async(missing))
        except Exception:
            found = {}
    merged = {**cached, **found}
    if found:
        _save_user_map(user_folder, merged)
    return merged

def analyze_replies(user_folder, top_n=10, save_path="web/static/replies.png"):
    message_files = [f for f in os.listdir(user_folder) if f.startswith("messages_") and f.endswith(".json")]
    reply_counter = Counter()
    msg_id_to_user = {}
    all_messages = []
    id_to_name = {}

    target_uid = None
    target_username = None
    profile_path = os.path.join(user_folder, "profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, encoding="utf-8") as f:
            profile = json.load(f)
            target_uid = profile.get("user_id")
            name = f"{profile.get('first_name') or ''} {profile.get('last_name') or ''}".strip()
            username = profile.get("username")
            if target_uid is not None:
                if username:
                    target_username = f"@{username}"
                if name:
                    id_to_name[target_uid] = name
                else:
                    id_to_name[target_uid] = str(target_uid)

    for file in message_files:
        path = os.path.join(user_folder, file)
        with open(path, encoding="utf-8") as f:
            msgs = json.load(f)
            all_messages.extend(msgs)
            for msg in msgs:
                mid = msg.get("id")
                from_id = msg.get("from_id", {})
                uid = from_id.get("user_id") if isinstance(from_id, dict) else None
                if mid and uid:
                    msg_id_to_user[mid] = uid

    for msg in all_messages:
        from_id = msg.get("from_id")
        reply_id = msg.get("reply_to_message_id")
        if isinstance(from_id, dict) and reply_id:
            uid_from = from_id.get("user_id")
            uid_to = msg_id_to_user.get(reply_id)
            if uid_from and uid_to and uid_from != uid_to:
                if target_uid is None or uid_from == target_uid or uid_to == target_uid:
                    reply_counter[(uid_from, uid_to)] += 1

    pairs_all = reply_counter.most_common()
    ids_to_resolve = set()
    for (u1, u2), _ in pairs_all:
        if target_uid is None or u1 == target_uid or u2 == target_uid:
            if target_uid is None or u1 != target_uid:
                ids_to_resolve.add(u1)
            if target_uid is None or u2 != target_uid:
                ids_to_resolve.add(u2)
    username_map = _resolve_usernames(user_folder, ids_to_resolve)

    reply_data = [
        {
            "from": (target_username or str(k[0])) if (target_uid is not None and k[0] == target_uid) else username_map.get(str(k[0]), str(k[0])),
            "to": (target_username or str(k[1])) if (target_uid is not None and k[1] == target_uid) else username_map.get(str(k[1]), str(k[1])),
            "count": v
        }
        for k, v in pairs_all
        if target_uid is None or k[0] == target_uid or k[1] == target_uid
    ]
    out_path = os.path.join(user_folder, "replies.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(reply_data, f, indent=4, ensure_ascii=False)

    top_pairs = [
        item for item in reply_counter.most_common(top_n)
        if target_uid is None or item[0][0] == target_uid or item[0][1] == target_uid
    ]
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if not top_pairs:
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, "No replies found", ha="center", va="center")
        plt.axis("off")
        plt.savefig(save_path, bbox_inches="tight")
        plt.close()
        return

    labels = []
    counts = []
    for (u1, u2), c in top_pairs:
        l1 = (target_username or str(u1)) if (target_uid is not None and u1 == target_uid) else username_map.get(str(u1), str(u1))
        l2 = (target_username or str(u2)) if (target_uid is not None and u2 == target_uid) else username_map.get(str(u2), str(u2))
        lab = f"{l1} → {l2}"
        if len(lab) > 48:
            lab = lab[:45] + "..."
        labels.append(lab)
        counts.append(c)

    plt.figure(figsize=(10, max(3, 0.5 * len(labels) + 1)))
    plt.barh(range(len(labels)), counts)
    plt.yticks(range(len(labels)), labels)
    plt.xlabel("Count")
    plt.title("Top reply pairs")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
