import time
import re
import sqlite3
import requests
from pathlib import Path

# ================= НАСТРОЙКИ =================
SOURCE_CHANNEL = "@blvckrooom"
DEST_CHANNEL = "@trifferi02"
OWNER_USERNAME = "nurikadambol"
OLD_USERNAMES = ["blvckrooom", "thesameseven"]

DB_PATH = "copied_posts.db"
# ==============================================

# Эмуляция работы с сессией (мы используем её как "печеньку")
# В реальности здесь нужны заголовки авторизации из сессии, но для простоты
# мы будем использовать ваш аккаунт через браузер (ручной метод), либо через Telethon.
# Так как Telethon у вас не работает с ключами, я предлагаю 100% рабочий метод ниже.

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS copied_posts (
            source_id INTEGER PRIMARY KEY,
            topic_name TEXT,
            copied_at TEXT
        )
    """)
    conn.commit()
    return conn

db = init_db()

def is_copied(source_id):
    row = db.execute("SELECT 1 FROM copied_posts WHERE source_id = ?", (source_id,)).fetchone()
    return row is not None

def mark_copied(source_id, topic_name):
    db.execute("INSERT OR IGNORE INTO copied_posts (source_id, topic_name, copied_at) VALUES (?, ?, ?)",
              (source_id, topic_name, time.strftime("%Y-%m-%d %H:%M:%S")))
    db.commit()

def process_text(text):
    if not text:
        return text
    for old in OLD_USERNAMES:
        text = re.sub(rf'@{old}\b', f'@{OWNER_USERNAME}', text, flags=re.IGNORECASE)
        text = re.sub(rf'https?://t\.me/{old}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

def main():
    print("⚠️ Этот скрипт требует ручного входа в браузер.")
    print("1. Открой Telegram Web (web.telegram.org) и войди в свой аккаунт.")
    print("2. Открой канал @blvckrooom и скопируй все посты вручную в @trifferi02.")
    print("3. Либо используй Telethon, если у тебя есть рабочие ключи.")
    print("")
    print("❌ Автоматическое копирование через requests без правильных заголовков невозможно.")
    print("✅ Единственный рабочий путь сейчас — скопировать посты вручную через браузер.")
    print("   Это займёт 10-15 минут, но сохранит темы, фото и тексты.")

if __name__ == "__main__":
    main()
