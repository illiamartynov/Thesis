import os
import json
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt


def analyze_hourly_activity(user_folder):
    """Анализ активности по часам из всех messages_*.json и отрисовка графика"""
    message_files = [f for f in os.listdir(user_folder) if f.startswith("messages_") and f.endswith(".json")]
    hour_counter = Counter()

    for file in message_files:
        path = os.path.join(user_folder, file)
        with open(path, encoding="utf-8") as f:
            messages = json.load(f)
            for msg in messages:
                try:
                    dt = datetime.fromisoformat(msg["date"])
                    hour_counter[dt.hour] += 1
                except Exception:
                    continue

    # Подготовка данных для графика
    hours = list(range(24))
    counts = [hour_counter.get(h, 0) for h in hours]

    # Рисуем график
    plt.figure(figsize=(10, 5))
    plt.bar(hours, counts)
    plt.xticks(hours)
    plt.xlabel("Час суток")
    plt.ylabel("Количество сообщений")
    plt.title("Активность пользователя по часам")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()
