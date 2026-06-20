import asyncio
import threading
import http.server
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

# Твои данные
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHAT_ID = -1002433118546
TARGET_CHAT_ID = -1002365330617

async def forward_message(update, context):
    if update.channel_post and update.channel_post.chat_id == SOURCE_CHAT_ID:
        await update.channel_post.copy(chat_id=TARGET_CHAT_ID)
        print("✅ Переслано!")

# Функция, которая запускает фейковый веб-сервер, чтобы Render не ругался
def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

# Запускаем фейковый сервер в отдельном потоке
threading.Thread(target=start_fake_server, daemon=True).start()

# Запускаем бота
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.Chat(SOURCE_CHAT_ID) & filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот запущен и готов к работе (порт 10000 открыт)!")
app.run_polling(allowed_updates=['channel_post'])
