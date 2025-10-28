import os
import sys
import json
from flask import Flask, render_template, redirect, url_for, request

# Добавляем src в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Импорты функций анализа
from analysis.activity import analyze_hourly_activity
from analysis.days import analyze_weekday_activity
from analysis.keywords import analyze_keywords
from analysis.interactions import analyze_mentions, analyze_replies

# Импорты поиска и сбора
from user_tools import (
    fetch_user_by_username,
    fetch_user_by_phone,
    fetch_user_messages_from_chat,
    fetch_user_messages_from_multiple_chats
)

# Flask конфигурация
app = Flask(
    __name__,
    template_folder="web/templates",
    static_folder="web/static"
)

DATA_DIR = "data"


@app.route("/")
def index():
    users = [f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))]
    return render_template("index.html", users=users)


@app.route("/profile/<username>")
def profile(username):
    folder = os.path.join(DATA_DIR, username)
    profile_path = os.path.join(folder, "profile.json")
    if not os.path.exists(profile_path):
        return f"Профиль {username} не найден", 404

    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)
    return render_template("profile.html", username=username, profile=profile)


@app.route("/activity/<username>")
def activity(username):
    folder = os.path.join(DATA_DIR, username)
    analyze_hourly_activity(folder, save_path="web/static/activity.png")
    return render_template("activity.html", username=username, image="activity.png")


@app.route("/days/<username>")
def days(username):
    folder = os.path.join(DATA_DIR, username)
    analyze_weekday_activity(folder, save_path="web/static/days.png")
    return render_template("activity.html", username=username, image="days.png")


@app.route("/keywords/<username>")
def keywords(username):
    folder = os.path.join(DATA_DIR, username)
    analyze_keywords(folder)
    return f"Анализ слов для {username} завершён."


@app.route("/mentions/<username>")
def mentions(username):
    folder = os.path.join(DATA_DIR, username)
    analyze_mentions(folder)
    return f"Анализ упоминаний для {username} завершён."


@app.route("/replies/<username>")
def replies(username):
    folder = os.path.join(DATA_DIR, username)
    analyze_replies(folder)
    return f"Анализ ответов для {username} завершён."


@app.route("/tools")
def tools():
    return render_template("search.html")


@app.route("/search_by_username", methods=["POST"])
def search_by_username():
    username = request.form["username"].strip()
    fetch_user_by_username(username)
    return redirect(url_for("profile", username=username))


@app.route("/search_by_phone", methods=["POST"])
def search_by_phone():
    phone = request.form["phone"].strip()
    fetch_user_by_phone(phone)
    return redirect("/")


@app.route("/collect_single_chat", methods=["POST"])
def collect_single_chat():
    user_username = request.form["user_username"].strip()
    chat_username = request.form["chat_username"].strip()
    fetch_user_messages_from_chat(user_username, chat_username)
    return redirect(url_for("profile", username=user_username))


@app.route("/collect_multiple_chats", methods=["POST"])
def collect_multiple_chats():
    user_username = request.form["user_username"].strip()
    raw = request.form["chat_usernames"].strip()
    chat_usernames = [s.strip() for s in raw.split(",") if s.strip()]
    fetch_user_messages_from_multiple_chats(user_username, chat_usernames)
    return redirect(url_for("profile", username=user_username))


if __name__ == "__main__":
    app.run(debug=True)
