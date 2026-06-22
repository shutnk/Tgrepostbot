import time
import re
import threading
import http.server
import requests
from flask import Flask

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
TARGET_CHANNEL = "@trifferi11"
NEW_AUTHOR = "@esen_baevich"
# ==============================================

# Flask для поддержки порта (Render не усыпит)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!", 200
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000), daemon=True).start()

# Буфер для ручного режима
pending_posts = {}

# Функция отправки сообщения в Telegram (через простые HTTP-запросы)
def send_telegram(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, data=data, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

# Функция получения обновлений (проверка сообщений)
def get_updates(offset=0):
    return send_telegram("getUpdates", {"offset": offset, "timeout": 30})

# Основной цикл бота (в синхронном режиме, без asyncio)
def main_loop():
    last_update_id = 0
    print("🚀 Бот запущен (синхронный)! Жду команды...")
    
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            if not updates or not updates.get("ok"):
                time.sleep(1)
                continue
            
            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                msg = update.get("message")
                if not msg:
                    continue
                
                user_id = msg["from"]["id"]
                text = msg.get("text", "")
                
                # Команда "Из темы: ..."
                if text.startswith("Из темы:"):
                    topic_name = text.replace("Из темы:", "").strip()
                    pending_posts[user_id] = {"topic": topic_name, "files": []}
                    send_telegram("sendMessage", {
                        "chat_id": user_id,
                        "text": f"✅ Тема '{topic_name}' выбрана! Отправь пост."
                    })
                    continue
                
                # Обработка активной темы
                if user_id in pending_posts:
                    topic_name = pending_posts[user_id]["topic"]
                    
                    # Если пришло фото
                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                        pending_posts[user_id]["files"].append(file_id)
                        continue
                    
                    # Если пришёл текст (подпись к альбому)
                    if text:
                        caption = re.sub(r'@\w+', NEW_AUTHOR, text)
                        time.sleep(2)  # Ждём все фото
                        
                        files = pending_posts[user_id]["files"]
                        if files:
                            # Отправляем все фото как альбом
                            media = [{"type": "photo", "media": fid} for fid in files]
                            send_telegram("sendMediaGroup", {
                                "chat_id": TARGET_CHANNEL,
                                "media": str(media).replace("'", '"'),
                                "caption": caption,
                                "message_thread_id": topic_name
                            })
                            send_telegram("sendMessage", {
                                "chat_id": user_id,
                                "text": f"✅ Альбом в тему '{topic_name}'!"
                            })
                        else:
                            send_telegram("sendMessage", {
                                "chat_id": TARGET_CHANNEL,
                                "text": caption,
                                "message_thread_id": topic_name
                            })
                        del pending_posts[user_id]
                
                # Небольшая задержка, чтобы не перегружать API
                time.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Ошибка в цикле: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
