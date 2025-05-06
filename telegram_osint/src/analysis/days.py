import os
import json
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt


def analyze_weekday_activity(user_folder):
    """Анализ активности по дням недели из всех messages_*.json и отрисовка графика"""
    message_files = [f for f in os.listdir(user_folder) if f.startswith("messages_") and f.endswith(".json")]
    weekday_counter = Counter()

    for file in message_files:
        path = os.path.join(user_folder, file)
        with open(path, encoding="utf-8") as f:
            messages = json.load(f)
            for msg in messages:
                try:
                    dt = datetime.fromisoformat(msg["date"])
                    weekday_counter[dt.weekday()] += 1  # Пн = 0, Вс = 6
                except Exception:
                    continue

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    counts = [weekday_counter.get(i, 0) for i in range(7)]

    plt.figure(figsize=(8, 5))
    plt.bar(weekdays, counts)
    plt.xlabel("День недели")
    plt.ylabel("Количество сообщений")
    plt.title("Активность пользователя по дням недели")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()
