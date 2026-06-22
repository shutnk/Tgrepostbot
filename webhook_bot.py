import re
import threading
import http.server
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, MessageHandler, filters

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
TARGET_CHANNEL = "@trifferi11"
NEW_AUTHOR = "@esen_baevich"
# ==============================================

# Фейковый сервер для Render
def run_fake_server():
    server = http.server.HTTPServer(("0.0.0.0", 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# Буфер для ручного режима
pending_posts = {}

def handle_forward(update, context):
    if update.message:
        msg = update.message
        user_id = msg.from_user.id
        
        # Если команда "Из темы: ..."
        if msg.text and msg.text.startswith("Из темы:"):
            topic_name = msg.text.replace("Из темы:", "").strip()
            pending_posts[user_id] = {"topic": topic_name, "files": []}
            msg.reply_text(f"✅ Тема '{topic_name}' выбрана! Отправь пост.")
            return
        
        # Если активная тема
        if user_id in pending_posts:
            topic_name = pending_posts[user_id]["topic"]
            
            if msg.photo:
                pending_posts[user_id]["files"].append(msg.photo[-1].file_id)
                return
            
            if msg.text:
                caption = re.sub(r'@\w+', NEW_AUTHOR, msg.text)
                import time
                time.sleep(2)
                
                files = pending_posts[user_id]["files"]
                if files:
                    media_group = [InputMediaPhoto(media=fid) for fid in files]
                    context.bot.send_media_group(
                        chat_id=TARGET_CHANNEL,
                        media=media_group,
                        caption=caption,
                        message_thread_id=topic_name
                    )
                    msg.reply_text(f"✅ Альбом в тему '{topic_name}'!")
                else:
                    context.bot.send_message(
                        chat_id=TARGET_CHANNEL,
                        text=caption,
                        message_thread_id=topic_name
                    )
                del pending_posts[user_id]

# Запуск через Application (без asyncio, синхронно)
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_forward))
    
    print("🚀 Бот запущен (версия 20.7)! Жду команды 'Из темы:'...")
    app.run_polling(allowed_updates=['message'])

if __name__ == "__main__":
    main()
