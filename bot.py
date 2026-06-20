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
            new_caption = re.sub(r'@\w+', NEW_AUTHOR, original_text)

            try:
                # 1. Сначала копируем сообщение как есть (альбом сохраняется!)
                sent_msg = await post.copy(chat_id=TARGET_CHANNEL)
                
                # 2. Если мы скопировали сообщение и у него есть ID, мы можем отредактировать подпись
                # (Обрати внимание: sent_msg - это объект отправленного сообщения)
                if sent_msg:
                    await context.bot.edit_message_caption(
                        chat_id=TARGET_CHANNEL,
                        message_id=sent_msg.message_id,
                        caption=new_caption
                    )
                    print(f"✅ Альбом скопирован, подпись заменена на {NEW_AUTHOR}")
                else:
                    # Если по какой-то причине не получилось отредактировать, отправляем как есть
                    print("⚠️ Альбом скопирован, но подпись не изменилась.")
            except Exception as e:
                print(f"❌ Ошибка пересылки: {e}")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот готов! Альбомы сохраняются, ник заменяется.")
app.run_polling(allowed_updates=['channel_post'])
