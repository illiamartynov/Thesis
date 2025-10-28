import asyncio
import json
import os
import time
from datetime import datetime

from tg_client import client
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently, UserStatusLastMonth, UserStatusLastWeek
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import PeerUser
import nest_asyncio
nest_asyncio.apply()


async def _get_user_by_phone(phone):
    contact = InputPhoneContact(client_id=0, phone=phone, first_name="Not Known", last_name="Not Known")
    result = await client(ImportContactsRequest([contact]))
    user = result.users[0] if result.users else None
    await client(DeleteContactsRequest(id=[user]))
    return user


async def _get_user_by_username(username):
    user = await client.get_entity(username)
    return user


def format_status(status):
    if isinstance(status, UserStatusOnline):
        return f"Online (until {status.expires.strftime('%Y-%m-%d %H:%M:%S')})"
    elif isinstance(status, UserStatusOffline):
        return f"Last seen at {status.was_online.strftime('%Y-%m-%d %H:%M:%S')}"
    elif isinstance(status, UserStatusRecently):
        return "Last seen recently"
    elif isinstance(status, UserStatusLastWeek):
        return "Last seen this week"
    elif isinstance(status, UserStatusLastMonth):
        return "Last seen this month"
    elif status is None:
        return "Status is hidden"
    else:
        return str(status)


def save_user_profile(user, full_user):
    data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "phone": user.phone,
        "bio": getattr(full_user.full_user, "about", "—"),
        "status": format_status(user.status)
    }

    username = user.username.lstrip("@") if user.username else None
    folder_name = username or str(user.id)

    path = os.path.join("data", folder_name)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "profile.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


async def download_avatar(user):
    if user.photo:
        username = user.username.lstrip("@") if user.username else None
        folder_name = username or str(user.id)
        os.makedirs(f"data/{folder_name}/avatars", exist_ok=True)
        path = f"data/{folder_name}/avatars/{user.id}.jpg"
        await client.download_profile_photo(user, file=path)


def fetch_user_by_username(username):
    async def run():
        await client.start()
        user = await _get_user_by_username(username)
        if user:
            full_user = await client(GetFullUserRequest(user.id))
            await download_avatar(user)
            save_user_profile(user, full_user)
            print(f"[+] User profile {user.username or user.id} saved.")
        else:
            print("User not found.")
        await client.disconnect()
    asyncio.run(run())


def fetch_user_by_phone(phone):
    async def run():
        await client.start()
        user = await _get_user_by_phone(phone)
        if user:
            full_user = await client(GetFullUserRequest(user.id))
            await download_avatar(user)
            save_user_profile(user, full_user)
            print(f"[+] User profile {user.username or user.id} saved.")
        else:
            print("User not found.")
        await client.disconnect()
    asyncio.run(run())


def _serialize_message(message):
    def safe_to_dict(obj):
        try:
            d = obj.to_dict()
            for k, v in d.items():
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
            return d
        except:
            return str(obj)

    return {
        "id": message.id,
        "date": message.date.isoformat() if message.date else None,
        "edit_date": message.edit_date.isoformat() if getattr(message, "edit_date", None) else None,
        "text": message.text,
        "from_id": message.from_id.to_dict() if message.from_id else None,
        "reply_to_message_id": getattr(message, "reply_to_msg_id", None),
        "media_type": type(message.media).__name__ if message.media else None,
        "fwd_from": safe_to_dict(message.fwd_from) if message.fwd_from else None,
        "entities": [e.to_dict() for e in message.entities] if message.entities else None,
        "reply_markup": safe_to_dict(message.reply_markup) if message.reply_markup else None
    }


def fetch_user_messages_from_chat(user_username, chat_username, limit=500000):
    async def run():
        await client.start()
        user = await _get_user_by_username(user_username)
        if not user:
            print("User not found.")
            return

        messages = []
        async for message in client.iter_messages(chat_username, limit=limit, reverse=True):
            if message.from_id and isinstance(message.from_id, PeerUser):
                messages.append(_serialize_message(message))

        username = user.username.lstrip("@") if user.username else None
        folder_name = username or str(user.id)
        os.makedirs("data/" + folder_name, exist_ok=True)
        with open(f"data/{folder_name}/messages_{chat_username}.json", "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)

        print(f"[+] Total messages: {len(messages)} in @{chat_username}")
        await client.disconnect()
    asyncio.run(run())


def fetch_user_messages_from_multiple_chats(user_username, chat_usernames: list, limit=500000):
    async def run():
        await client.start()
        user = await _get_user_by_username(user_username)
        if not user:
            print("User not found.")
            return

        username = user.username.lstrip("@") if user.username else None
        folder_name = username or str(user.id)
        os.makedirs("data/" + folder_name, exist_ok=True)
        total_messages = 0
        total_chats = len(chat_usernames)
        total_start = time.perf_counter()

        for i, chat_username in enumerate(chat_usernames, 1):
            print(f"\n[{i}/{total_chats}] [{datetime.now().strftime('%H:%M:%S')}] Processing @{chat_username}...")
            start = time.perf_counter()
            messages = []
            try:
                async for message in client.iter_messages(chat_username, limit=limit, reverse=True):
                    if message.from_id and isinstance(message.from_id, PeerUser):
                        messages.append(_serialize_message(message))

                with open(f"data/{folder_name}/messages_{chat_username}.json", "w", encoding="utf-8") as f:
                    json.dump(messages, f, indent=4, ensure_ascii=False)

                duration = time.perf_counter() - start
                print(f"[+] @{chat_username}: {len(messages)} messages saved in {duration:.2f} sec.")
                total_messages += len(messages)

            except Exception as e:
                print(f"[!] Error processing @{chat_username}: {e}")

        total_duration = time.perf_counter() - total_start
        print(f"\n✅ Completed: {total_chats} chats, {total_messages} messages in {total_duration:.2f} sec.")
        await client.disconnect()

    asyncio.run(run())
