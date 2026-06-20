import asyncio
import threading
import http.server
import re
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
NEW_AUTHOR = "@esen_baevich"

# Хранилище для сборки альбомов
pending_albums = {}

async def forward_message(update, context):
    global pending_albums
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            post = update.channel_post
            
            # Если это альбом (фото)
            if post.photo and post.media_group_id:
                group_id = post.media_group_id
                file_id = post.photo[-1].file_id
                
                # Сохраняем текст из первого пришедшего поста
                if group_id not in pending_albums:
                    pending_albums[group_id] = {
                        "files": [],
                        "text": post.caption or ""
                    }
                
                pending_albums[group_id]["files"].append(file_id)
                
                # Создаём задачу на отправку, если это первое фото
                if len(pending_albums[group_id]["files"]) == 1:
                    asyncio.create_task(process_album(group_id, context))
            
            # Одиночное фото
            elif post.photo:
                # Меняем @ники в тексте
                new_caption = re.sub(r'@\w+', NEW_AUTHOR, post.caption or "")
                await context.bot.send_photo(
                    chat_id=TARGET_CHANNEL,
                    photo=post.photo[-1].file_id,
                    caption=new_caption
                )
                print("✅ Одиночное фото переслано с заменой текста.")

async def process_album(group_id, context):
    global pending_albums
    # Ждём 3 секунды, чтобы подтянулись остальные части альбома
    await asyncio.sleep(3)
    
    # Забираем данные из буфера
    album_data = pending_albums.get(group_id)
    if not album_data:
        return
    
    files = album_data["files"]
    original_text = album_data["text"]
    
    # Формируем медиа-группу
    media_group = [InputMediaPhoto(media=fid) for fid in files]
    
    # Меняем все @ники на @esen_baevich в тексте
    new_text = re.sub(r'@\w+', NEW_AUTHOR, original_text)
    
    # Отправляем альбом с обновлённым текстом
    await context.bot.send_media_group(
        chat_id=TARGET_CHANNEL,
        media=media_group,
        caption=new_text
    )
    print(f"✅ Собран альбом из {len(files)} фото. Текст заменён на {NEW_AUTHOR}")
    
    # Очищаем буфер
    del pending_albums[group_id]

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот запущен! Альбомы склеиваются, текст и @ники меняются.")
app.run_polling(allowed_updates=['channel_post'])
