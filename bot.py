import asyncio
import threading
import http.server
import re
from telegram import Bot, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@trifferi098"
TARGET_CHANNEL = "@trifferi097"
NEW_AUTHOR = "@esen_baevich"

async def forward_message(update, context):
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            post = update.channel_post
            
            # Текст с заменой @ников
            original_text = post.caption or post.text or ""
            new_caption = re.sub(r'@\w+', NEW_AUTHOR, original_text)

            try:
                # ===== СПЕЦИАЛЬНЫЙ БЛОК ДЛЯ АЛЬБОМОВ (МНОГО ФОТО/ВИДЕО) =====
                # Если у поста есть медиа-группа (альбом)
                if post.media_group_id:
                    # Мы не можем получить все фото из одного update, 
                    # поэтому отправляем как есть, но с новой подписью.
                    # Бот сам соберет альбом, если отправить через send_media_group.
                    
                    media_group = []
                    if post.photo:
                        media_group.append(InputMediaPhoto(media=post.photo[-1].file_id))
                    elif post.video:
                        media_group.append(InputMediaVideo(media=post.video.file_id))
                    
                    # Отправляем как группу (Telegram сам соберет в альбом)
                    await context.bot.send_media_group(
                        chat_id=TARGET_CHANNEL,
                        media=media_group,
                        caption=new_caption  # Подпись прикрепится к первому фото
                    )
                    print(f"✅ Альбом переслан с подписью: {NEW_AUTHOR}")
                
                # ===== ОБЫЧНЫЕ ПОСТЫ (ОДНО ФОТО, ВИДЕО ИЛИ ТЕКСТ) =====
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
                    await context.bot.send_message(
                        chat_id=TARGET_CHANNEL,
                        text=new_caption
                    )
                else:
                    await post.copy(chat_id=TARGET_CHANNEL, caption=new_caption)
                
                print(f"✅ Пост переслан. Ник заменён на {NEW_AUTHOR}")

            except Exception as e:
                print(f"❌ Ошибка пересылки: {e}")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот готов! Поддерживает альбомы и замену @ на @esen_baevich!")
app.run_polling(allowed_updates=['channel_post'])
