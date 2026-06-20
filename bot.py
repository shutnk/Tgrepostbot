import asyncio
import threading
import http.server
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
NEW_AUTHOR = "@esen_baevich"

async def forward_message(update, context):
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            post = update.channel_post
            
            try:
                # 1. Копируем альбом (или одно фото) БЕЗ ТЕКСТА
                # Telegram сам соберёт все фото в одну группу, если caption пустой
                await post.copy(
                    chat_id=TARGET_CHANNEL,
                    caption=""  # Пустая подпись = чистый альбом
                )
                print("✅ Альбом скопирован!")
                
                # 2. Отправляем отдельное сообщение с контактом
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=f"📞 Для консультации и заказа:\n{NEW_AUTHOR}"
                )
                print(f"✅ Контакт {NEW_AUTHOR} отправлен отдельно!")
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот работает: копирует альбом + отправляет контакт отдельно.")
app.run_polling(allowed_updates=['channel_post'])
