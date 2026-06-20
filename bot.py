import asyncio
import threading
import http.server
import re
from telegram import Bot, InputMediaPhoto
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
                # ===== ГЛАВНОЕ ИЗМЕНЕНИЕ =====
                # Если у сообщения есть media_group_id (это альбом)
                if post.media_group_id:
                    # Запрашиваем у Telegram все фотографии из этого альбома
                    album_photos = await context.bot.get_media_group(
                        chat_id=post.chat_id,
                        message_id=post.message_id
                    )
                    
                    # Собираем их в список для отправки
                    media_group = []
                    for msg in album_photos:
                        if msg.photo:
                            media_group.append(InputMediaPhoto(media=msg.photo[-1].file_id))
                    
                    # Отправляем целый альбом с новой подписью
                    await context.bot.send_media_group(
                        chat_id=TARGET_CHANNEL,
                        media=media_group,
                        caption=new_caption
                    )
                    print(f"✅ Альбом из {len(media_group)} фото отправлен с подписью {NEW_AUTHOR}")

                # ===== Обычные посты =====
                elif post.photo:
                    await context.bot.send_photo(
                        chat_id=TARGET_CHANNEL,
                        photo=post.photo[-1].file_id,
                        caption=new_caption
                    )
                elif post.video:
                    await context.bot.send_video(
                        chat_id=TARGET_CHANNEL,
                        video=post.video.file_id,
                        caption=new_caption
                    )
                elif post.text:
                    new_text = re.sub(r'@\w+', NEW_AUTHOR, post.text)
                    await context.bot.send_message(
                        chat_id=TARGET_CHANNEL,
                        text=new_text
                    )
                else:
                    await post.copy(chat_id=TARGET_CHANNEL, caption=new_caption)
                
                print("✅ Пост обработан.")
            
            except Exception as e:
                print(f"❌ Ошибка: {e}")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот с ПРАВИЛЬНОЙ СБОРКОЙ АЛЬБОМОВ запущен!")
app.run_polling(allowed_updates=['channel_post'])
