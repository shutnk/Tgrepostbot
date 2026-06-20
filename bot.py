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
                
                # Добавляем фото в буфер
                if group_id not in pending_albums:
                    pending_albums[group_id] = []
                pending_albums[group_id].append(file_id)
                
                # Создаём задачу на отправку, если это первое фото
                if len(pending_albums[group_id]) == 1:
                    asyncio.create_task(process_album(group_id, context))
            
            # Одиночное фото
            elif post.photo:
                caption = re.sub(r'@\w+', NEW_AUTHOR, post.caption or "")
                await context.bot.send_photo(
                    chat_id=TARGET_CHANNEL,
                    photo=post.photo[-1].file_id,
                    caption=caption
                )
                print("✅ Одиночное фото переслано.")

async def process_album(group_id, context):
    global pending_albums
    # Ждём 3 секунды, чтобы подтянулись остальные части альбома
    await asyncio.sleep(3)
    
    # Забираем все собранные фото
    files = pending_albums.get(group_id, [])
    if not files:
        return
    
    # Формируем медиа-группу (без подписи внутри, подпись добавим позже)
    media_group = [InputMediaPhoto(media=fid) for fid in files]
    
    # Отправляем альбом
    await context.bot.send_media_group(
        chat_id=TARGET_CHANNEL,
        media=media_group,
        caption=f"📞 Для консультации и заказа:\n{NEW_AUTHOR}"
    )
    print(f"✅ Собран альбом из {len(files)} фото с подписью {NEW_AUTHOR}")
    
    # Очищаем буфер
    del pending_albums[group_id]

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот с автосборкой альбомов запущен!")
app.run_polling(allowed_updates=['channel_post'])
