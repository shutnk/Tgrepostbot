import asyncio
import threading
import http.server
import re
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
            original_text = post.caption or post.text or ""
            
            # 1. Сначала копируем пост как есть (вместе с альбомом!) — это 100% сохраняет группировку
            await post.copy(chat_id=TARGET_CHANNEL)
            
            # 2. Отправляем подпись отдельным сообщением сразу под скопированным постом
            signature_text = f"📞 Для консультации и заказа: {NEW_AUTHOR}"
            if original_text:
                # Если в посте был текст, дублируем его (с заменой ника)
                new_text = re.sub(r'@\w+', NEW_AUTHOR, original_text)
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=f"{new_text}\n\n{signature_text}"
                )
            else:
                # Если пост был без текста, просто кидаем подпись
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=signature_text
                )
            
            print(f"✅ Пост скопирован. Подпись {NEW_AUTHOR} отправлена следом!")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот работает! Альбомы сохраняются, подпись идёт следом.")
app.run_polling(allowed_updates=['channel_post'])
