import os
import json
import string
from collections import Counter
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

def analyze_keywords(user_folder, top_n=20, save_path="web/static/keywords.png"):
    """Analyze keywords in user messages and save chart to file"""
    message_files = [f for f in os.listdir(user_folder) if f.startswith("messages_") and f.endswith(".json")]
    all_words = []

    russian_stopwords = set(stopwords.words("russian"))
    translator = str.maketrans("", "", string.punctuation + "«»…“”")

    for file in message_files:
        path = os.path.join(user_folder, file)
        with open(path, encoding="utf-8") as f:
            messages = json.load(f)
            for msg in messages:
                text = msg.get("text")
                if not isinstance(text, str):
                    continue
                text = text.lower().translate(translator)
                words = text.split()
                words = [
                    w for w in words
                    if w not in russian_stopwords and len(w) > 2 and not w.isdigit()
                ]
                all_words.extend(words)

    counter = Counter(all_words)

    # Save JSON result
    out_path = os.path.join(user_folder, "keywords_top.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(counter.most_common(top_n), f, indent=4, ensure_ascii=False)

    # Visualization
    top_words = counter.most_common(top_n)
    if top_words:
        words, counts = zip(*top_words)
        plt.figure(figsize=(10, 5))
        plt.bar(words, counts)
        plt.xticks(rotation=45, ha="right")
        plt.xlabel("Words")
        plt.ylabel("Frequency")
        plt.title("Keyword Frequency Analysis")
        plt.tight_layout()
        plt.grid(axis="y", linestyle="--", alpha=0.5)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()
