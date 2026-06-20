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

# Хранилище для временных альбомов (ключ: media_group_id, значение: список фото)
albums = {}

async def forward_message(update, context):
    global albums
    if update.channel_post:
        if update.channel_post.chat.username == SOURCE_CHANNEL.replace("@", ""):
            post = update.channel_post
            original_text = post.caption or post.text or ""
            new_caption = re.sub(r'@\w+', NEW_AUTHOR, original_text)

            # ЕСЛИ ЭТО ФОТО (может быть частью альбома)
            if post.photo:
                group_id = post.media_group_id
                file_id = post.photo[-1].file_id

                # Если это альбом (у него есть media_group_id)
                if group_id:
                    # Добавляем фото в список альбома
                    if group_id not in albums:
                        albums[group_id] = []
                    albums[group_id].append(file_id)

                    # Если это первое фото в альбоме, запускаем таймер на 2 секунды
                    if len(albums[group_id]) == 1:
                        await asyncio.sleep(2.5)  # Ждём, пока придут остальные фото
                        
                        # Собираем медиа-группу
                        media_group = []
                        for fid in albums[group_id]:
                            media_group.append(InputMediaPhoto(media=fid))
                        
                        # Отправляем полноценный альбом (с подписью к первому фото)
                        await context.bot.send_media_group(
                            chat_id=TARGET_CHANNEL,
                            media=media_group,
                            caption=new_caption
                        )
                        print(f"✅ ГРУППА ИЗ {len(albums[group_id])} ФОТО ОТПРАВЛЕНА! Подпись: {NEW_AUTHOR}")
                        
                        # Очищаем память, чтобы не копить мусор
                        del albums[group_id]
                else:
                    # Если это одно фото без альбома
                    await context.bot.send_photo(
                        chat_id=TARGET_CHANNEL,
                        photo=file_id,
                        caption=new_caption
                    )
                    print("✅ Одно фото переслано.")

            # ЕСЛИ ЭТО ВИДЕО
            elif post.video:
                await context.bot.send_video(
                    chat_id=TARGET_CHANNEL,
                    video=post.video.file_id,
                    caption=new_caption
                )
                print("✅ Видео переслано.")
            
            # ЕСЛИ ЭТО ТЕКСТ
            elif post.text:
                new_text = re.sub(r'@\w+', NEW_AUTHOR, post.text)
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=new_text
                )
                print("✅ Текст переслан.")
            
            # ОСТАЛЬНЫЕ ТИПЫ
            else:
                await post.copy(chat_id=TARGET_CHANNEL, caption=new_caption)
                print("✅ Другое скопировано.")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот с УМНОЙ ГРУППИРОВКОЙ ФОТО запущен!")
app.run_polling(allowed_updates=['channel_post'])
