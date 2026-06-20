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
                
                if group_id not in pending_albums:
                    pending_albums[group_id] = []
                pending_albums[group_id].append(file_id)
                
                if len(pending_albums[group_id]) >= 2:
                    await process_album(group_id, context)
            
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

async def process_album(group_id, context):
    global pending_albums
    files = pending_albums.pop(group_id, [])
    if not files: return
    
    media_group = [InputMediaPhoto(media=fid) for fid in files]
    await context.bot.send_media_group(
        chat_id=TARGET_CHANNEL,
        media=media_group
    )
    print(f"✅ Альбом из {len(files)} фото отправлен!")

# ============================================
# ДВОЙНОЙ СЕРВЕР (Порт 10000 для Telegram и Порт 80 для UptimeRobot)
# ============================================
class FakeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_dual_server():
    # Слушаем порт 80 (для UptimeRobot)
    try:
        with socketserver.TCPServer(("0.0.0.0", 80), FakeHandler) as httpd:
            print("✅ Порт 80 открыт для UptimeRobot (будильник)")
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
    except Exception as e:
        print("⚠️ Порт 80 занят, но это не страшно")
    
    # Слушаем порт 10000 (для Telegram Webhook)
    server = http.server.HTTPServer(('0.0.0.0', 10000), FakeHandler)
    server.serve_forever()

threading.Thread(target=start_dual_server, daemon=True).start()
# ============================================

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот запущен! UptimeRobot будет будить через порт 80.")
app.run_polling(allowed_updates=['channel_post'])
