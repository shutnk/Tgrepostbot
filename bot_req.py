import time
import re
import requests
import sqlite3

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"
DEST_CHANNEL = "@trifferi02"
OWNER_USERNAME = "nurikadambol"
OLD_USERNAMES = ["blvckrooom", "thesameseven"]

DB_PATH = "posted.db"
# ==============================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posted_messages (
            source_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    return conn

db = init_db()

def is_posted(source_id):
    row = db.execute("SELECT 1 FROM posted_messages WHERE source_id = ?", (source_id,)).fetchone()
    return row is not None

def mark_posted(source_id):
    db.execute("INSERT OR IGNORE INTO posted_messages (source_id) VALUES (?)", (source_id,))
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

def tg_request(method, data=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, data=data, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return None

def get_updates(offset=0):
    return tg_request("getUpdates", {"offset": offset, "timeout": 30})

def main():
    print("🚀 Запуск бота через прямые API-запросы...")
    
    source_info = tg_request("getChat", {"chat_id": SOURCE_CHANNEL})
    if not source_info or not source_info.get("ok"):
        print("❌ Не удалось получить ID канала", SOURCE_CHANNEL)
        return
    source_id = source_info["result"]["id"]
    
    last_update_id = 0
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            if not updates or not updates.get("ok"):
                time.sleep(1)
                continue
            
            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                
                if "channel_post" not in update:
                    continue
                
                msg = update["channel_post"]
                if msg.get("chat", {}).get("id") != source_id:
                    continue
                
                msg_id = msg["message_id"]
                if is_posted(msg_id):
                    continue
                
                text = process_text(msg.get("text") or msg.get("caption") or "")
                
                try:
                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                        tg_request("sendPhoto", {
                            "chat_id": DEST_CHANNEL,
                            "photo": file_id,
                            "caption": text
                        })
                    elif "video" in msg:
                        file_id = msg["video"]["file_id"]
                        tg_request("sendVideo", {
                            "chat_id": DEST_CHANNEL,
                            "video": file_id,
                            "caption": text
                        })
                    elif "document" in msg:
                        file_id = msg["document"]["file_id"]
                        tg_request("sendDocument", {
                            "chat_id": DEST_CHANNEL,
                            "document": file_id,
                            "caption": text
                        })
                    elif text:
                        tg_request("sendMessage", {
                            "chat_id": DEST_CHANNEL,
                            "text": text
                        })
                    
                    mark_posted(msg_id)
                    print(f"✅ Пост #{msg_id} скопирован")
                    
                except Exception as e:
                    print(f"❌ Ошибка отправки: {e}")
                
                time.sleep(1)
            
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
