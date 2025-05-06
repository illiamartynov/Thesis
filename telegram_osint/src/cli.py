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
        print("Нет сохранённых пользователей. Используй пункты 1–4, чтобы добавить нового.")
        return None

    print("\nСуществующие пользователи:")
    for i, name in enumerate(folders, 1):
        print(f"{i}. {name}")
    print("0. Ввести нового пользователя")

    choice = input("Выбери пользователя или 0 для нового: ").strip()
    if choice == "0":
        return None
    try:
        idx = int(choice) - 1
        return os.path.join(base_path, folders[idx])
    except:
        print("Некорректный выбор.")
        return None


def cli_menu():
    while True:
        print("\nTelegram OSINT CLI")
        print("1. Поиск по username")
        print("2. Поиск по номеру телефона")
        print("3. Сбор сообщений пользователя в чате (один)")
        print("4. Сбор сообщений пользователя в нескольких чатах")
        print("5. Анализ активности по времени (график)")
        print("6. Анализ активности по дням недели (график)")
        print("7. Частотный анализ слов (без AI)")
        print("8. Анализ упоминаний @username")
        print("9. Анализ кому отвечает пользователь (reply)")
        print("0. Выход")

        choice = input("Выбери опцию: ")
        if choice == "1":
            username = input("Введите username (без @): ")
            fetch_user_by_username(username)
        elif choice == "2":
            phone = input("Введите номер (в формате +123456789): ")
            fetch_user_by_phone(phone)
        elif choice == "3":
            user_username = input("Введите username пользователя (без @): ")
            chat_username = input("Введите username чата/группы (без @): ")
            fetch_user_messages_from_chat(user_username, chat_username)
        elif choice == "4":
            user_username = input("Введите username пользователя (без @): ")
            raw_chats = input("Введите username чатов через запятую (без @): ")
            chat_usernames = [chat.strip() for chat in raw_chats.split(",") if chat.strip()]
            fetch_user_messages_from_multiple_chats(user_username, chat_usernames)
        elif choice == "5":
            user_folder = select_user_folder()
            if user_folder:
                analyze_hourly_activity(user_folder)
            else:
                print("OSINT можно запустить через пункты 1–4 для нового пользователя.")
        elif choice == "6":
            user_folder = select_user_folder()
            if user_folder:
                analyze_weekday_activity(user_folder)
            else:
                print("OSINT можно запустить через пункты 1–4 для нового пользователя.")
        elif choice == "7":
            user_folder = select_user_folder()
            if user_folder:
                analyze_keywords(user_folder)
            else:
                print("OSINT можно запустить через пункты 1–4 для нового пользователя.")
        elif choice == "8":
            user_folder = select_user_folder()
            if user_folder:
                analyze_mentions(user_folder)
            else:
                print("OSINT можно запустить через пункты 1–4 для нового пользователя.")
        elif choice == "9":
            user_folder = select_user_folder()
            if user_folder:
                analyze_replies(user_folder)
            else:
                print("OSINT можно запустить через пункты 1–4 для нового пользователя.")
        elif choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод, попробуй снова.")
