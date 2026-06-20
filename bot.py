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
            
            # Если это альбом (медиа-группа) - делаем сложную магию
            if post.media_group_id:
                try:
                    # 1. Запоминаем ID группы и первую картинку
                    group_id = post.media_group_id
                    media_list = []
                    
                    # Берём первую картинку
                    if post.photo:
                        media_list.append(InputMediaPhoto(
                            media=post.photo[-1].file_id,
                            caption=None  # Пока без подписи
                        ))
                    
                    # 2. Даём Telegram время, чтобы подтянуть остальные фото
                    # (Это критически важно, иначе увидим только первую)
                    await asyncio.sleep(2.5) 
                    
                    # 3. Просим бота дать нам ВСЕ обновления за последние секунды
                    updates = await context.bot.get_updates(limit=10)
                    
                    # 4. Ищем в этих обновлениях фото с таким же media_group_id
                    for upd in updates:
                        if upd.channel_post and upd.channel_post.media_group_id == group_id:
                            if upd.channel_post.photo and upd.channel_post.message_id != post.message_id:
                                # Добавляем остальные фото в список
                                media_list.append(InputMediaPhoto(
                                    media=upd.channel_post.photo[-1].file_id
                                ))
                    
                    # 5. Готовим финальную подпись
                    original_text = post.caption or post.text or ""
                    new_caption = re.sub(r'@\w+', NEW_AUTHOR, original_text)
                    
                    # 6. Отправляем собранный альбом! (Теперь он 100% целый)
                    await context.bot.send_media_group(
                        chat_id=TARGET_CHANNEL,
                        media=media_list,
                        caption=new_caption  # Подпись прикрепляется к первому фото
                    )
                    print(f"✅ АЛЬБОМ СОБРАН! ({len(media_list)} фото) Автор заменён на {NEW_AUTHOR}")
                    
                except Exception as e:
                    print(f"❌ Ошибка сборки альбома: {e}")
            
            # Если это обычный пост (1 фото или текст) - просто пересылаем
            elif post.photo:
                original_text = post.caption or post.text or ""
                new_caption = re.sub(r'@\w+', NEW_AUTHOR, original_text)
                await context.bot.send_photo(
                    chat_id=TARGET_CHANNEL,
                    photo=post.photo[-1].file_id,
                    caption=new_caption
                )
                print("✅ 1 фото переслано.")
            elif post.text:
                new_text = re.sub(r'@\w+', NEW_AUTHOR, post.text)
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=new_text
                )
                print("✅ Текст переслан.")
            else:
                await post.copy(chat_id=TARGET_CHANNEL)
                print("✅ Другое скопировано.")

def start_fake_server():
    server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_fake_server, daemon=True).start()

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот с магией альбомов запущен! Жди 3 секунды для сборки.")
app.run_polling(allowed_updates=['channel_post'])
