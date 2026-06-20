import asyncio
import threading
import http.server
import http.client
import re
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
NEW_AUTHOR = "@esen_baevich"

# ==========================================
# БУДИЛЬНИК (Keep-Alive) — каждые 10 минут
# ==========================================
def wake_up():
    while True:
        try:
            # Отправляем запрос самому себе, чтобы Render видел активность
            conn = http.client.HTTPConnection("tgrepostbot.onrender.com", 10000, timeout=5)
            conn.request("GET", "/")
            conn.close()
            print("⏰ Будильник: сервер жив!")
        except:
            pass
        # Спим 10 минут (600 секунд)
        time.sleep(600)

# Запускаем будильник в отдельном потоке
import time
threading.Thread(target=wake_up, daemon=True).start()
# ==========================================

# Буфер для альбомов
pending_albums = {}

async def forward_message(update, context):
    global pending_albums
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            post = update.channel_post
            
            # ЕСЛИ ЭТО АЛЬБОМ
            if post.photo and post.media_group_id:
                group_id = post.media_group_id
                file_id = post.photo[-1].file_id
                
                if group_id not in pending_albums:
                    pending_albums[group_id] = {
                        "files": [],
                        "text": post.caption or ""
                    }
                pending_albums[group_id]["files"].append(file_id)
                
                if len(pending_albums[group_id]["files"]) >= 4:
                    await process_album(group_id, context)
            
            # ОДИНОЧНОЕ ФОТО
            elif post.photo:
                new_caption = re.sub(r'@\w+', NEW_AUTHOR, post.caption or "")
                await context.bot.send_photo(
                    chat_id=TARGET_CHANNEL,
                    photo=post.photo[-1].file_id,
                    caption=new_caption
                )
                print("✅ Одиночное фото переслано.")

            # ТЕКСТ
            elif post.text:
                new_text = re.sub(r'@\w+', NEW_AUTHOR, post.text)
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=new_text
                )
                print("✅ Текст переслан.")

async def process_album(group_id, context):
    global pending_albums
    album_data = pending_albums.get(group_id)
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
    print(f"✅ Собран альбом из {len(files)} фото!")
    del pending_albums[group_id]

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот запущен! Встроенный будильник будет будить его каждые 10 минут.")
app.run_polling(allowed_updates=['channel_post'])
