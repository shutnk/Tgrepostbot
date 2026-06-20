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

# Хранилище для временных альбомов
albums = {}

async def forward_message(update, context):
    global albums
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            post = update.channel_post
            original_text = post.caption or post.text or ""
            new_caption = re.sub(r'@\w+', NEW_AUTHOR, original_text)

            # Если это фото
            if post.photo:
                group_id = post.media_group_id
                file_id = post.photo[-1].file_id

                # Если это альбом
                if group_id:
                    if group_id not in albums:
                        albums[group_id] = []
                    albums[group_id].append(file_id)

                    # Если это первое фото в альбоме, запускаем таймер
                    if len(albums[group_id]) == 1:
                        # ================== ВРЕМЯ ОЖИДАНИЯ (6 СЕКУНД) ==================
                        await asyncio.sleep(6)  # Увеличили с 2.5 до 6 секунд
                        
                        media_group = []
                        for fid in albums[group_id]:
                            media_group.append(InputMediaPhoto(media=fid))
                        
                        await context.bot.send_media_group(
                            chat_id=TARGET_CHANNEL,
                            media=media_group,
                            caption=new_caption
                        )
                        print(f"✅ ГРУППА ИЗ {len(albums[group_id])} ФОТО ОТПРАВЛЕНА! Подпись: {NEW_AUTHOR}")
                        del albums[group_id]
                else:
                    # Одиночное фото
                    await context.bot.send_photo(
                        chat_id=TARGET_CHANNEL,
                        photo=file_id,
                        caption=new_caption
                    )
                    print("✅ Одно фото переслано.")

            # Видео
            elif post.video:
                await context.bot.send_video(
                    chat_id=TARGET_CHANNEL,
                    video=post.video.file_id,
                    caption=new_caption
                )
                print("✅ Видео переслано.")
            
            # Текст
            elif post.text:
                new_text = re.sub(r'@\w+', NEW_AUTHOR, post.text)
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=new_text
                )
                print("✅ Текст переслан.")
            
            # Остальные типы
            else:
                await post.copy(chat_id=TARGET_CHANNEL, caption=new_caption)
                print("✅ Другое скопировано.")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот с УВЕЛИЧЕННЫМ ВРЕМЕНЕМ ОЖИДАНИЯ (6 сек) запущен!")
app.run_polling(allowed_updates=['channel_post'])
