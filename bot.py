import asyncio
import threading
import http.server
import re  # Модуль для регулярных выражений
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
NEW_AUTHOR = "@esen_baevich"  # Ник, на который будем заменять

async def forward_message(update, context):
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            post = update.channel_post
            
            # Берём текст или подпись
            original_text = post.caption or post.text or ""
            
            # Регулярное выражение: ищем слово, которое начинается с @ и состоит из букв, цифр и подчеркиваний
            # Это заменит ЛЮБОЙ @никнейм в тексте на NEW_AUTHOR
            new_text = re.sub(r'@\w+', NEW_AUTHOR, original_text)

            try:
                # Если это картинка
                if post.photo:
                    await context.bot.send_photo(
                        chat_id=TARGET_CHANNEL,
                        photo=post.photo[-1].file_id,
                        caption=new_text
                    )
                # Если это видео
                elif post.video:
                    await context.bot.send_video(
                        chat_id=TARGET_CHANNEL,
                        video=post.video.file_id,
                        caption=new_text
                    )
                # Если это обычный текст
                elif post.text:
                    await context.bot.send_message(
                        chat_id=TARGET_CHANNEL,
                        text=new_text
                    )
                else:
                    await post.copy(chat_id=TARGET_CHANNEL, caption=new_text)
                
                print(f"✅ Переслано. Ник заменён на {NEW_AUTHOR}")
            except Exception as e:
                print(f"❌ Ошибка пересылки: {e}")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот готов! Все @ники будут заменены на @esen_baevich!")
app.run_polling(allowed_updates=['channel_post'])
