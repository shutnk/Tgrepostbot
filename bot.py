import asyncio
import threading
import http.server
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
YOUR_ID = 5468112563  # Твой ID

async def forward_message(update, context):
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            # Копируем пост, но добавляем подпись
            await update.channel_post.copy(
                chat_id=TARGET_CHANNEL,
                caption=f"{update.channel_post.caption or ''}\n\n📌 Автор: [Ваше имя](tg://user?id={YOUR_ID})"
            )
            print("✅ Переслано с подписью!")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот готов (с подписью автора)!")
app.run_polling(allowed_updates=['channel_post'])
