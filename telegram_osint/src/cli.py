import os
from tg_client import client
from user_tools import (
    fetch_user_by_username,
    fetch_user_by_phone,
    fetch_user_messages_from_chat,
    fetch_user_messages_from_multiple_chats
)
from analysis.activity import analyze_hourly_activity
from analysis.days import analyze_weekday_activity
from analysis.keywords import analyze_keywords
from analysis.interactions import analyze_mentions, analyze_replies


def select_user_folder():
    base_path = "data"
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    if not folders:
        print("No saved users found. Use options 1–4 to add a new one.")
        return None

    print("\nExisting users:")
    for i, name in enumerate(folders, 1):
        print(f"{i}. {name}")
    print("0. Enter a new user")

    choice = input("Choose a user or 0 to add a new one: ").strip()
    if choice == "0":
        return None
    try:
        idx = int(choice) - 1
        return os.path.join(base_path, folders[idx])
    except:
        print("Invalid choice.")
        return None


def cli_menu():
    while True:
        print("\nTelegram OSINT CLI")
        print("1. Search by username")
        print("2. Search by phone number")
        print("3. Collect messages in a single chat")
        print("4. Collect messages in multiple chats")
        print("5. Analyze activity by hour (chart)")
        print("6. Analyze activity by weekday (chart)")
        print("7. Keyword frequency analysis (no AI)")
        print("8. Analyze @username mentions")
        print("9. Analyze reply relationships (who replies to whom)")
        print("0. Exit")

        choice = input("Choose an option: ")
        if choice == "1":
            username = input("Enter username (without @): ")
            fetch_user_by_username(username)
        elif choice == "2":
            phone = input("Enter phone number (+123456789 format): ")
            fetch_user_by_phone(phone)
        elif choice == "3":
            user_username = input("Enter the user's username (without @): ")
            chat_username = input("Enter chat/group username (without @): ")
            fetch_user_messages_from_chat(user_username, chat_username)
        elif choice == "4":
            user_username = input("Enter the user's username (without @): ")
            raw_chats = input("Enter chat usernames separated by commas (without @): ")
            chat_usernames = [chat.strip() for chat in raw_chats.split(",") if chat.strip()]
            fetch_user_messages_from_multiple_chats(user_username, chat_usernames)
        elif choice == "5":
            user_folder = select_user_folder()
            if user_folder:
                analyze_hourly_activity(user_folder)
            else:
                print("OSINT can be run via options 1–4 for a new user.")
        elif choice == "6":
            user_folder = select_user_folder()
            if user_folder:
                analyze_weekday_activity(user_folder)
            else:
                print("OSINT can be run via options 1–4 for a new user.")
        elif choice == "7":
            user_folder = select_user_folder()
            if user_folder:
                analyze_keywords(user_folder)
            else:
                print("OSINT can be run via options 1–4 for a new user.")
        elif choice == "8":
            user_folder = select_user_folder()
            if user_folder:
                analyze_mentions(user_folder)
            else:
                print("OSINT can be run via options 1–4 for a new user.")
        elif choice == "9":
            user_folder = select_user_folder()
            if user_folder:
                analyze_replies(user_folder)
            else:
                print("OSINT can be run via options 1–4 for a new user.")
        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid input, try again.")
