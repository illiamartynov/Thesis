import os
import json
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
import matplotlib

matplotlib.use('Agg')  # Для работы без GUI

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def analyze_weekday_activity(folder, save_path="web/static/days.png"):
    message_files = [f for f in os.listdir(folder) if f.startswith("messages_") and f.endswith(".json")]
    weekday_counter = Counter()

    for filename in message_files:
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            messages = json.load(f)
            for msg in messages:
                date_str = msg.get("date")
                if date_str:
                    try:
                        dt = datetime.fromisoformat(date_str)
                        weekday = dt.strftime("%A")
                        weekday_counter[weekday] += 1
                    except Exception:
                        continue

    values = [weekday_counter.get(day, 0) for day in WEEKDAYS]

    plt.figure(figsize=(10, 5))
    plt.bar(WEEKDAYS, values, color="#4c78a8")
    plt.title("Activity by Weekday")
    plt.xlabel("Weekday")
    plt.ylabel("Messages")
    plt.xticks(rotation=45)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
