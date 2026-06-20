import asyncio
import threading
import http.server
import socketserver
import re
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
NEW_AUTHOR = "@esen_baevich"

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
                
                # Сохраняем текст из первого пришедшего поста
                if group_id not in pending_albums:
                    pending_albums[group_id] = {
                        "files": [],
                        "text": post.caption or ""
                    }
                
                pending_albums[group_id]["files"].append(file_id)
                
                # ЗАПУСКАЕМ ТАЙМЕР ТОЛЬКО ОДИН РАЗ (при первом фото)
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
    # Даём время Telegram подтянуть ВСЕ фото (даже если их 10 штук)
    await asyncio.sleep(3)
    
    album_data = pending_albums.pop(group_id, None)
    if not album_data:
        return
    
    files = album_data["files"]
    original_text = album_data["text"]
    
    # Меняем @ники в тексте
    new_text = re.sub(r'@\w+', NEW_AUTHOR, original_text)
    
    # Собираем медиа-группу
    media_group = [InputMediaPhoto(media=fid) for fid in files]
    
    # ОТПРАВЛЯЕМ АЛЬБОМ С ТЕКСТОМ (caption прикрепляется к первому фото)
    await context.bot.send_media_group(
        chat_id=TARGET_CHANNEL,
        media=media_group,
        caption=new_text
    )
    print(f"✅ Альбом из {len(files)} фото отправлен с текстом!")

# ============================================
# ДВОЙНОЙ СЕРВЕР (Порт 80 и 10000)
# ============================================
class FakeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_dual_server():
    try:
        with socketserver.TCPServer(("0.0.0.0", 80), FakeHandler) as httpd:
            print("✅ Порт 80 открыт для UptimeRobot")
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
    except:
        pass
    
    server = http.server.HTTPServer(('0.0.0.0', 10000), FakeHandler)
    server.serve_forever()

threading.Thread(target=start_dual_server, daemon=True).start()
# ============================================

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот с универсальным сборщиком (2-10 фото) запущен!")
app.run_polling(allowed_updates=['channel_post'])
