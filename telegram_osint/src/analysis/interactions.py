import os
import json
import re
from collections import Counter
from telethon.tl.types import PeerUser
from tg_client import client


def analyze_mentions(user_folder, top_n=20):
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

    print(f"\n🔗 Top-{top_n} mentioned users:")
    for mention, count in mention_counter.most_common(top_n):
        print(f"{mention:<20} {count}")

    if mention_counter:
        out_path = os.path.join(user_folder, "mentions.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(mention_counter.most_common(), f, indent=4, ensure_ascii=False)
        print(f"\n✅ Mentions saved to: {out_path}")
    else:
        print("❗ No mentions found.")


def analyze_replies(user_folder, top_n=10):
    async def run():
        await client.start()

        message_files = [f for f in os.listdir(user_folder) if f.startswith("messages_") and f.endswith(".json")]
        reply_counter = Counter()
        msg_id_to_user = {}
        all_users = set()
        all_messages = []

        id_to_name = {}
        profile_path = os.path.join(user_folder, "profile.json")
        if os.path.exists(profile_path):
            with open(profile_path, encoding="utf-8") as f:
                profile = json.load(f)
                uid = profile.get("user_id")
                name = f"{profile.get('first_name') or ''} {profile.get('last_name') or ''}".strip()
                username = profile.get("username")
                if name:
                    id_to_name[uid] = f"{name} ({username})" if username else f"{name} ({uid})"
                elif username:
                    id_to_name[uid] = f"{username} ({uid})"
                else:
                    id_to_name[uid] = str(uid)

        for file in message_files:
            path = os.path.join(user_folder, file)
            with open(path, encoding="utf-8") as f:
                msgs = json.load(f)
                all_messages.extend(msgs)
                for msg in msgs:
                    msg_id = msg.get("id")
                    from_id = msg.get("from_id", {})
                    uid = from_id.get("user_id") if isinstance(from_id, dict) else None
                    if msg_id and uid:
                        msg_id_to_user[msg_id] = uid
                        all_users.add(uid)

        for msg in all_messages:
            from_user = msg.get("from_id")
            reply_id = msg.get("reply_to_message_id")
            if isinstance(from_user, dict) and reply_id:
                user_id = from_user.get("user_id")
                replied_to_user = msg_id_to_user.get(reply_id)

                if not replied_to_user:
                    try:
                        chat_name = None
                        for file in message_files:
                            path = os.path.join(user_folder, file)
                            with open(path, encoding="utf-8") as f:
                                check_msgs = json.load(f)
                                if any(m.get("id") == msg.get("id") for m in check_msgs):
                                    chat_name = file[len("messages_"):-len(".json")]
                                    break

                        if chat_name:
                            entity = await client.get_entity(chat_name)
                            reply_msg = await client.get_messages(entity, ids=reply_id)
                            if reply_msg and isinstance(reply_msg.from_id, PeerUser):
                                replied_to_user = reply_msg.from_id.user_id
                                msg_id_to_user[reply_id] = replied_to_user
                                all_users.add(replied_to_user)
                    except Exception as e:
                        print(f"[!] Failed to fetch message #{reply_id}: {e}")
                        continue

                if user_id and replied_to_user and user_id != replied_to_user:
                    reply_counter[(user_id, replied_to_user)] += 1

        for uid in all_users:
            if uid not in id_to_name:
                try:
                    entity = await client.get_entity(uid)
                    first_name = getattr(entity, 'first_name', '') or ''
                    last_name = getattr(entity, 'last_name', '') or ''
                    full_name = f"{first_name} {last_name}".strip()
                    username = getattr(entity, 'username', None)
                    if full_name:
                        id_to_name[uid] = f"{full_name} ({username})" if username else f"{full_name} ({uid})"
                    elif username:
                        id_to_name[uid] = f"{username} ({uid})"
                    else:
                        id_to_name[uid] = str(uid)
                except:
                    id_to_name[uid] = str(uid)

        print(f"\n↩️ Top-{top_n} reply pairs:")
        if reply_counter:
            for (uid1, uid2), count in reply_counter.most_common(top_n):
                name1 = id_to_name.get(uid1, str(uid1))
                name2 = id_to_name.get(uid2, str(uid2))
                print(f"{name1} → {name2:<25} {count}")

            out_path = os.path.join(user_folder, "replies.json")
            reply_data = [
                {"from": id_to_name.get(uid1, str(uid1)), "to": id_to_name.get(uid2, str(uid2)), "count": count}
                for (uid1, uid2), count in reply_counter.most_common()
            ]
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(reply_data, f, indent=4, ensure_ascii=False)
            print(f"\n✅ Replies saved to: {out_path}")
        else:
            print("❗ No replies found.")

        await client.disconnect()

    client.loop.run_until_complete(run())
