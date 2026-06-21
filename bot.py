import asyncio
import threading
import re
from flask import Flask
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHAT_ID = -1002414824426  # ID группы @trifferi11 (с минусом!)
TARGET_CHANNEL = "@trifferi097"
NEW_AUTHOR = "@esen_baevich"

# ===== Flask-сервер (чтобы Render не спал) =====
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!", 200

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000, threaded=True)

threading.Thread(target=run_flask, daemon=True).start()
# ==============================================

# Буфер для альбомов
pending_albums = {}

async def forward_message(update, context):
    global pending_albums
    post = update.channel_post or update.message
    
    if not post:
        return

    # Проверяем, что сообщение из нашей группы (по ID)
    if post.chat_id == SOURCE_CHAT_ID:
        
        # Игнорируем служебные системные сообщения (создание топиков и т.д.)
        if post.is_topic_message is False and post.text in ["Topic was created", "was created"]:
            return
        
        # 1. Обработка Альбома (несколько фото)
        if post.photo and post.media_group_id:
            group_id = post.media_group_id
            file_id = post.photo[-1].file_id
            
            # Сохраняем текст из первого пришедшего фото
            if group_id not in pending_albums:
                pending_albums[group_id] = {
                    "files": [],
                    "text": post.caption or ""
                }
            
            pending_albums[group_id]["files"].append(file_id)
            
            # Запускаем таймер только один раз на первый элемент
            if len(pending_albums[group_id]["files"]) == 1:
                asyncio.create_task(process_album_after_delay(group_id, context))
        
        # 2. Одиночное фото
        elif post.photo:
            new_caption = re.sub(r'@\w+', NEW_AUTHOR, post.caption or "")
            await context.bot.send_photo(
                chat_id=TARGET_CHANNEL,
                photo=post.photo[-1].file_id,
                caption=new_caption
            )
            print("✅ Одиночное фото переслано из топика!")
        
        # 3. Текстовое сообщение
        elif post.text:
            new_text = re.sub(r'@\w+', NEW_AUTHOR, post.text)
            await context.bot.send_message(
                chat_id=TARGET_CHANNEL,
                text=new_text
            )
            print("✅ Текст переслан из топика!")

async def process_album_after_delay(group_id, context):
    global pending_albums
    await asyncio.sleep(3)
    
    album_data = pending_albums.pop(group_id, None)
    if not album_data:
        return
    
    files = album_data["files"]
    original_text = album_data["text"]
    new_text = re.sub(r'@\w+', NEW_AUTHOR, original_text)
    
    media_group = [InputMediaPhoto(media=fid) for fid in files]
    
    await context.bot.send_media_group(
        chat_id=TARGET_CHANNEL,
        media=media_group,
        caption=new_text
    )
    print(f"✅ Альбом из {len(files)} фото переслан из топика!")

# Запуск бота
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, forward_message))
print("🚀 Бот запущен! Следит за всеми разделами группы @trifferi11.")
app.run_polling(allowed_updates=['message', 'channel_post'])
