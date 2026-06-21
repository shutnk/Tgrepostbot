import asyncio
import threading
import re
from flask import Flask
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, MessageHandler, filters

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
TARGET_CHANNEL = "@trifferi11"
NEW_AUTHOR = "@esen_baevich"
# ==============================================

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is alive!", 200
threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000, threaded=True), daemon=True).start()

# Буфер для ожидания сообщений
pending_posts = {}

async def handle_forward(update, context):
    if update.message:
        msg = update.message
        user_id = msg.from_user.id
        
        # Если это команда "Из темы: ..."
        if msg.text and msg.text.startswith("Из темы:"):
            topic_name = msg.text.replace("Из темы:", "").strip()
            # Запоминаем, что этот пользователь хочет отправить в эту тему
            pending_posts[user_id] = {"topic": topic_name, "files": []}
            await msg.reply_text(f"✅ Тема '{topic_name}' выбрана! Теперь отправь пост с фото.")
            return
        
        # Если у пользователя есть активная тема
        if user_id in pending_posts:
            topic_name = pending_posts[user_id]["topic"]
            
            # Если это фото — добавляем в буфер
            if msg.photo:
                pending_posts[user_id]["files"].append(msg.photo[-1].file_id)
                return  # Ждём остальные фото
            
            # Если это текст (подпись) — сохраняем и отправляем альбом
            if msg.text:
                caption = re.sub(r'@\w+', NEW_AUTHOR, msg.text)
                # Ждём 2 секунды, чтобы гарантировать, что все фото пришли
                await asyncio.sleep(2)
                
                files = pending_posts[user_id]["files"]
                if files:
                    media_group = [InputMediaPhoto(media=fid) for fid in files]
                    await context.bot.send_media_group(
                        chat_id=TARGET_CHANNEL,
                        media=media_group,
                        caption=caption,
                        message_thread_id=topic_name
                    )
                    await msg.reply_text(f"✅ Альбом отправлен в тему '{topic_name}'!")
                else:
                    await context.bot.send_message(
                        chat_id=TARGET_CHANNEL,
                        text=caption,
                        message_thread_id=topic_name
                    )
                # Удаляем пользователя из буфера
                del pending_posts[user_id]
                return

# Запуск
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_forward))

print("🚀 Бот с ручным режимом и альбомами запущен!")
app.run_polling(allowed_updates=['message'])
