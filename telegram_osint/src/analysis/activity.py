import os
import json
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt


def analyze_hourly_activity(user_folder, save_path=None):
    """
    Analyze user activity by hour based on all messages_*.json files in the user folder.
    If save_path is provided — saves the chart, otherwise displays it.
    """
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

    hours = list(range(24))
    counts = [hour_counter.get(h, 0) for h in hours]

    plt.figure(figsize=(10, 5))
    plt.bar(hours, counts, color="skyblue")
    plt.xticks(hours)
    plt.xlabel("Hour of day")
    plt.ylabel("Number of messages")
    plt.title("User activity by hour")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()
