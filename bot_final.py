import time
import re
import requests
import json
import sqlite3

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"
DEST_CHANNEL = "@trifferi02"
OWNER_USERNAME = "nurikadambol"

DB_PATH = "posted.db"
# ==============================================

def init_db():
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

db = init_db()

def is_posted(source_msg_id, source_chat_id):
    cursor = db.cursor()
    cursor.execute(
        "SELECT 1 FROM posted_messages WHERE source_id = ? AND source_chat_id = ?",
        (source_msg_id, source_chat_id)
    )
    return cursor.fetchone() is not None

def save_posted(source_msg_id, dest_msg_id, source_chat_id):
    cursor = db.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO posted_messages (source_id, dest_id, source_chat_id, posted_at) VALUES (?, ?, ?, ?)",
        (source_msg_id, dest_msg_id, source_chat_id, time.strftime("%Y-%m-%d %H:%M:%S"))
    )
    db.commit()

def tg_request(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, data=data, timeout=30)
        return resp.json()
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return None

def process_text(text):
    if not text:
        return ""
    text = re.sub(r'@blvckrooom\b', f'@{OWNER_USERNAME}', text, flags=re.IGNORECASE)
    text = re.sub(r'@thesameseven\b', f'@{OWNER_USERNAME}', text, flags=re.IGNORECASE)
    text = re.sub(r'https?://t\.me/\S+', '', text, flags=re.IGNORECASE)
    return text.strip()

def main():
    print("🚀 Запуск финального бота (без Telethon)...")
    
    source_info = tg_request("getChat", {"chat_id": SOURCE_CHANNEL})
    if not source_info or not source_info.get("ok"):
        print("❌ Не удалось получить ID канала", SOURCE_CHANNEL)
        return
    source_chat_id = source_info["result"]["id"]
    
    last_update_id = 0
    
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
                
                try:
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
                        print(f"✅ Пост #{msg_id} скопирован")
                    else:
                        print(f"❌ Ошибка отправки поста #{msg_id}: {resp}")
                    
                except Exception as e:
                    print(f"❌ Ошибка отправки: {e}")
                
                time.sleep(1)
            
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
