import asyncio
import threading
import re
from flask import Flask
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
NEW_AUTHOR = "@esen_baevich"

# ===== Flask-сервер (чтобы UptimeRobot видел 200 OK) =====
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!", 200  # Отдаём 200 OK

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000, threaded=True)

threading.Thread(target=run_flask, daemon=True).start()
# =====================================================

# Буфер для альбомов
pending_albums = {}

async def forward_message(update, context):
    global pending_albums
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            post = update.channel_post
            
            if post.photo and post.media_group_id:
                group_id = post.media_group_id
                file_id = post.photo[-1].file_id
                
                if group_id not in pending_albums:
                    pending_albums[group_id] = {
                        "files": [],
                        "text": post.caption or ""
                    }
                
                pending_albums[group_id]["files"].append(file_id)
                
                if len(pending_albums[group_id]["files"]) == 1:
                    asyncio.create_task(process_album_after_delay(group_id, context))
            
            elif post.photo:
                new_caption = re.sub(r'@\w+', NEW_AUTHOR, post.caption or "")
                await context.bot.send_photo(
                    chat_id=TARGET_CHANNEL,
                    photo=post.photo[-1].file_id,
                    caption=new_caption
                )
            
            elif post.text:
                new_text = re.sub(r'@\w+', NEW_AUTHOR, post.text)
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=new_text
                )

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
    print(f"✅ Альбом из {len(files)} фото отправлен!")

# Запуск основного бота (Polling)
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот с реальным Flask-сервером запущен! UptimeRobot теперь покажет 200 OK.")
app.run_polling(allowed_updates=['channel_post'])
