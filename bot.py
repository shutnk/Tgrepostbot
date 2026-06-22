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

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!", 200
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000), daemon=True).start()

# Храним состояние пользователя: тему + файлы
user_state = {}

def tg_request(method, data=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, data=data, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def get_updates(offset=0):
    return tg_request("getUpdates", {"offset": offset, "timeout": 30})

def create_topic(topic_name):
    # Создаём тему (если есть — Telegram вернёт ошибку, мы её игнорируем)
    return tg_request("createForumTopic", {
        "chat_id": TARGET_CHANNEL,
        "name": topic_name
    })

def main_loop():
    last_update_id = 0
    print("🚀 Бот запущен! Создаёт темы, собирает альбомы и копирует подписи...")

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

                # 1. Команда для установки темы
                if text.startswith("Из темы:"):
                    topic_name = text.replace("Из темы:", "").strip()
                    if topic_name.lower() == "general":
                        tg_request("sendMessage", {
                            "chat_id": user_id,
                            "text": "❌ Игнорирую General. Укажи другую тему."
                        })
                        continue

                    # Создаём тему (если нет) и сохраняем состояние
                    create_topic(topic_name)
                    user_state[user_id] = {"topic": topic_name, "files": [], "caption": None}
                    tg_request("sendMessage", {
                        "chat_id": user_id,
                        "text": f"✅ Тема '{topic_name}' создана/выбрана! Отправляй фото и текст."
                    })
                    continue

                # 2. Если пользователь в процессе
                if user_id in user_state:
                    state = user_state[user_id]

                    # Если пришло фото — добавляем в альбом
                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                        state["files"].append(file_id)
                        continue

                    # Если пришёл текст — это подпись ко всему альбому
                    if text:
                        state["caption"] = re.sub(r'@\w+', NEW_AUTHOR, text)

                        # Ждём 3 секунды, чтобы Telegram подтянул все фото
                        time.sleep(3)

                        # Если есть фото — отправляем альбомом
                        if state["files"]:
                            media = [{"type": "photo", "media": fid} for fid in state["files"]]
                            tg_request("sendMediaGroup", {
                                "chat_id": TARGET_CHANNEL,
                                "media": str(media).replace("'", '"'),
                                "caption": state["caption"] or "",
                                "message_thread_id": state["topic"]
                            })
                            tg_request("sendMessage", {
                                "chat_id": user_id,
                                "text": f"✅ Альбом отправлен в тему '{state['topic']}'!"
                            })
                        else:
                            # Если фото не пришли — просто текст
                            tg_request("sendMessage", {
                                "chat_id": TARGET_CHANNEL,
                                "text": state["caption"],
                                "message_thread_id": state["topic"]
                            })

                        # Очищаем состояние
                        del user_state[user_id]

                time.sleep(0.5)

        except Exception as e:
            print(f"❌ Ошибка цикла: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
