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
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            # Если в посте есть текст (caption или просто текст)
            original_text = update.channel_post.caption or update.channel_post.text or ""
            
            # Добавляем подпись от твоего имени
            new_text = f"{original_text}\n\n📌 Автор: {YOUR_NICKNAME}"
            
            # Если это пост с картинкой/видео, копируем с подписью
            if update.channel_post.caption is not None:
                await update.channel_post.copy(
                    chat_id=TARGET_CHANNEL,
                    caption=new_text
                )
            # Если это просто текст, отправляем как текст с подписью
            else:
                await update.channel_post.copy(
                    chat_id=TARGET_CHANNEL,
                    caption=new_text
                )
            print("✅ Переслано с твоей подписью!")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот запущен! Подпись: @nurikadambol")
app.run_polling(allowed_updates=['channel_post'])
