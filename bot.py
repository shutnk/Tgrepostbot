import asyncio
import threading
import http.server
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
YOUR_NICKNAME = "@nurikadambol"  # Твой ник

async def forward_message(update, context):
    if update.channel_post:
        # Проверяем, что пост из нашего канала
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            
            # Получаем текст поста (или подпись к картинке) если есть
            original_text = update.channel_post.caption or update.channel_post.text or ""
            
            # Формируем подпись (твой ник внизу)
            new_caption = f"{original_text}\n\n✍️ {YOUR_NICKNAME}"
            
            # УНИВЕРСАЛЬНЫЙ МЕТОД: Копируем сообщение и ПРИНУДИТЕЛЬНО меняем caption
            await update.channel_post.copy(
                chat_id=TARGET_CHANNEL,
                caption=new_caption
            )
            print(f"✅ Переслано с подписью: {YOUR_NICKNAME}")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот готов! Подпись ставится принудительно.")
app.run_polling(allowed_updates=['channel_post'])
