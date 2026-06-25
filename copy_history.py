import time
import re
import requests
import sqlite3

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"
DEST_CHANNEL = "@trifferi02"
OWNER_USERNAME = "nurikadambol"

DB_PATH = "history.db"
# ==============================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            source_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    return conn

db = init_db()

def is_copied(source_id):
    cursor = db.cursor()
    cursor.execute("SELECT 1 FROM history WHERE source_id = ?", (source_id,))
    return cursor.fetchone() is not None

def mark_copied(source_id):
    cursor = db.cursor()
    cursor.execute("INSERT OR IGNORE INTO history (source_id) VALUES (?)", (source_id,))
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
    return text.strip()

def main():
    print("🚀 Сброс памяти бота и копирование всей истории...")
    
    # 1. Сбрасываем offset в 0 (бот "забывает" всё)
    tg_request("getUpdates", {"offset": 0, "limit": 1})
    time.sleep(2)
    
    # 2. Получаем ID исходного канала
    source_info = tg_request("getChat", {"chat_id": SOURCE_CHANNEL})
    if not source_info or not source_info.get("ok"):
        print("❌ Не удалось получить ID канала", SOURCE_CHANNEL)
        return
    source_chat_id = source_info["result"]["id"]
    
    # 3. Теперь получаем все посты как "новые"
    print("📥 Начинаю копирование всех постов...")
    last_update_id = 0
    total = 0
    
    while True:
        try:
            updates = tg_request("getUpdates", {"offset": last_update_id + 1, "timeout": 30})
            if not updates or not updates.get("ok"):
                break
            
            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                
                if "channel_post" not in update:
                    continue
                
                msg = update["channel_post"]
                if msg.get("chat", {}).get("id") != source_chat_id:
                    continue
                
                msg_id = msg["message_id"]
                if is_copied(msg_id):
                    continue
                
                text = msg.get("text") or msg.get("caption") or ""
                new_text = process_text(text)
                
                try:
                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                        tg_request("sendPhoto", {
                            "chat_id": DEST_CHANNEL,
                            "photo": file_id,
                            "caption": new_text
                        })
                    elif "video" in msg:
                        file_id = msg["video"]["file_id"]
                        tg_request("sendVideo", {
                            "chat_id": DEST_CHANNEL,
                            "video": file_id,
                            "caption": new_text
                        })
                    elif "document" in msg:
                        file_id = msg["document"]["file_id"]
                        tg_request("sendDocument", {
                            "chat_id": DEST_CHANNEL,
                            "document": file_id,
                            "caption": new_text
                        })
                    elif new_text:
                        tg_request("sendMessage", {
                            "chat_id": DEST_CHANNEL,
                            "text": new_text
                        })
                    
                    mark_copied(msg_id)
                    total += 1
                    print(f"✅ Скопирован пост #{msg_id}")
                    
                except Exception as e:
                    print(f"❌ Ошибка отправки: {e}")
                
                time.sleep(1)
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            break
    
    print(f"🎉 Готово! Всего скопировано {total} постов.")

if __name__ == "__main__":
    main()
