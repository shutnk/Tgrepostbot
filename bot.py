import os
import asyncio
import logging
import re
import time
import requests
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
SOURCE_CHANNEL = "@blvckrooom"
DEST_CHANNEL = "@trifferi02"
OWNER_USERNAME = "nurikadambol"
OLD_USERNAMES = ["blvckrooom", "thesameseven"]

DB_PATH = "posted.db"
# ==============================================

app = Flask(__name__)

def init_db():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posted_messages (
            source_id INTEGER PRIMARY KEY,
            dest_id INTEGER,
            source_chat_id INTEGER,
            posted_at TEXT
        )
    """)
    conn.commit()
    return conn

def is_posted(source_msg_id, source_chat_id):
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM posted_messages WHERE source_id = ? AND source_chat_id = ?",
        (source_msg_id, source_chat_id)
    )
    return cursor.fetchone() is not None

def save_posted(source_msg_id, dest_msg_id, source_chat_id):
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO posted_messages (source_id, dest_id, source_chat_id, posted_at) VALUES (?, ?, ?, ?)",
        (source_msg_id, dest_msg_id, source_chat_id, time.strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()

def tg_request(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, data=data, timeout=30)
        return resp.json()
    except Exception as e:
        logger.error(f"❌ Ошибка API: {e}")
        return None

def process_text(text):
    if not text:
        return ""
    for old in OLD_USERNAMES:
        text = re.sub(rf'@{old}\b', f'@{OWNER_USERNAME}', text, flags=re.IGNORECASE)
        text = re.sub(rf'https?://t\.me/{old}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

async def ensure_subscribed():
    try:
        chat_info = tg_request("getChat", {"chat_id": SOURCE_CHANNEL})
        if chat_info and chat_info.get("ok"):
            logger.info(f"✅ Бот уже в канале {SOURCE_CHANNEL}")
            return True
        
        result = tg_request("joinChannel", {"chat_id": SOURCE_CHANNEL})
        if result and result.get("ok"):
            logger.info(f"✅ Бот подписан на {SOURCE_CHANNEL}")
            return True
        else:
            logger.error(f"❌ Не удалось подписать бота на {SOURCE_CHANNEL}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка подписки: {e}")
        return False

async def process_updates():
    logger.info("🚀 Запуск бота через Bot API...")
    
    # Подписываем бота на канал
    await ensure_subscribed()
    
    # Получаем ID канала источника
    source_info = tg_request("getChat", {"chat_id": SOURCE_CHANNEL})
    if not source_info or not source_info.get("ok"):
        logger.error("❌ Не удалось получить ID канала", SOURCE_CHANNEL)
        return False
    source_chat_id = source_info["result"]["id"]
    
    last_update_id = 0
    total_copied = 0
    
    while True:
        try:
            updates = tg_request("getUpdates", {"offset": last_update_id + 1, "timeout": 30})
            if not updates or not updates.get("ok"):
                time.sleep(1)
                continue
            
            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                
                if "channel_post" not in update:
                    continue
                
                msg = update["channel_post"]
                msg_chat_id = msg.get("chat", {}).get("id")
                if msg_chat_id != source_chat_id:
                    continue
                
                msg_id = msg["message_id"]
                if is_posted(msg_id, msg_chat_id):
                    continue
                
                text = msg.get("text") or msg.get("caption") or ""
                new_text = process_text(text)
                
                # Определяем тему
                topic_name = "General"
                lower_text = new_text.lower()
                if "сумка" in lower_text or "bag" in lower_text:
                    topic_name = "Сумки"
                elif "обувь" in lower_text or "shoe" in lower_text:
                    topic_name = "Обувь"
                elif "куртка" in lower_text or "jacket" in lower_text:
                    topic_name = "Куртки"
                elif "кроссовки" in lower_text or "sneaker" in lower_text:
                    topic_name = "Кроссовки"
                elif "пальто" in lower_text or "coat" in lower_text:
                    topic_name = "Пальто"
                
                try:
                    resp = None
                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                        resp = tg_request("sendPhoto", {
                            "chat_id": DEST_CHANNEL,
                            "photo": file_id,
                            "caption": new_text
                        })
                    elif "video" in msg:
                        file_id = msg["video"]["file_id"]
                        resp = tg_request("sendVideo", {
                            "chat_id": DEST_CHANNEL,
                            "video": file_id,
                            "caption": new_text
                        })
                    elif "document" in msg:
                        file_id = msg["document"]["file_id"]
                        resp = tg_request("sendDocument", {
                            "chat_id": DEST_CHANNEL,
                            "document": file_id,
                            "caption": new_text
                        })
                    elif new_text:
                        resp = tg_request("sendMessage", {
                            "chat_id": DEST_CHANNEL,
                            "text": new_text
                        })
                    
                    if resp and resp.get("ok"):
                        dest_msg_id = resp["result"]["message_id"]
                        save_posted(msg_id, dest_msg_id, msg_chat_id)
                        total_copied += 1
                        logger.info(f"✅ Пост #{msg_id} скопирован (Всего: {total_copied})")
                    else:
                        logger.error(f"❌ Ошибка отправки поста #{msg_id}: {resp}")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки: {e}")
                
                time.sleep(1)
            
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            time.sleep(30)

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/health")
def health():
    asyncio.run(process_updates())
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
