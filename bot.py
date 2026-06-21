import asyncio
import re
import sqlite3
import logging
import threading
from datetime import datetime
from flask import Flask
from telegram import Bot, InputMediaPhoto, InputMediaVideo
from telegram.error import RetryAfter, TelegramError

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"          # Откуда берём
TARGET_CHANNEL = "@trifferi02"          # Куда отправляем
NEW_AUTHOR = "@esen_baevich"
DB_NAME = "posted_messages.db"
# ==============================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)

# ===== Flask-сервер (чтобы Render не спал) =====
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is alive!", 200
threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000, threaded=True), daemon=True).start()
# ==============================================

# База данных (чтобы не пересылать одно и то же дважды)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posted (
            source_id INTEGER PRIMARY KEY,
            target_id INTEGER,
            source_chat_id INTEGER,
            posted_at TEXT
        )
    """)
    conn.commit()
    return conn

db = init_db()

def is_posted(source_msg_id, source_chat_id):
    cursor = db.cursor()
    cursor.execute(
        "SELECT 1 FROM posted WHERE source_id = ? AND source_chat_id = ?",
        (source_msg_id, source_chat_id)
    )
    return cursor.fetchone() is not None

def save_posted(source_msg_id, target_msg_id, source_chat_id):
    cursor = db.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO posted VALUES (?, ?, ?, ?)",
        (source_msg_id, target_msg_id, source_chat_id, datetime.now().isoformat())
    )
    db.commit()

# Замена текста и @ников
def process_text(text, entities=None):
    if not text:
        return text, None

    # Заменяем ЛЮБОЙ @ник на @esen_baevich
    text = re.sub(r'@\w+', NEW_AUTHOR, text)

    # Удаление ссылок t.me (если есть)
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)

    return text, None

# Отправка сообщения в целевой канал
async def send_to_target(msg, target_chat_id):
    text, entities = process_text(
        msg.text or msg.caption or "",
        msg.entities if hasattr(msg, 'entities') and msg.entities else
            (msg.caption_entities if hasattr(msg, 'caption_entities') and msg.caption_entities else None)
    )

    try:
        if msg.photo:
            sent = await bot.send_photo(
                chat_id=target_chat_id,
                photo=msg.photo[-1].file_id,
                caption=text[:1024] if text else None,
                caption_entities=entities
            )
        elif msg.video:
            sent = await bot.send_video(
                chat_id=target_chat_id,
                video=msg.video.file_id,
                caption=text[:1024] if text else None,
                caption_entities=entities
            )
        elif msg.document:
            sent = await bot.send_document(
                chat_id=target_chat_id,
                document=msg.document.file_id,
                caption=text[:1024] if text else None,
                caption_entities=entities
            )
        elif msg.audio:
            sent = await bot.send_audio(
                chat_id=target_chat_id,
                audio=msg.audio.file_id,
                caption=text[:1024] if text else None,
                caption_entities=entities
            )
        elif msg.voice:
            sent = await bot.send_voice(
                chat_id=target_chat_id,
                voice=msg.voice.file_id,
                caption=text[:1024] if text else None,
                caption_entities=entities
            )
        elif msg.video_note:
            sent = await bot.send_video_note(
                chat_id=target_chat_id,
                video_note=msg.video_note.file_id
            )
        elif msg.sticker:
            sent = await bot.send_sticker(
                chat_id=target_chat_id,
                sticker=msg.sticker.file_id
            )
        elif msg.animation:
            sent = await bot.send_animation(
                chat_id=target_chat_id,
                animation=msg.animation.file_id,
                caption=text[:1024] if text else None,
                caption_entities=entities
            )
        else:
            sent = await bot.send_message(
                chat_id=target_chat_id,
                text=text
            )
        return sent.message_id

    except RetryAfter as e:
        logger.warning(f"FloodWait: {e.retry_after}с")
        raise
    except TelegramError as e:
        logger.error(f"Ошибка отправки: {e}")
        raise

# Отправка альбома (несколько медиа)
async def send_album_to_target(messages, target_chat_id):
    from telegram import InputMediaPhoto, InputMediaVideo

    media = []
    caption = None

    for i, msg in enumerate(messages):
        if i == 0:
            caption, _ = process_text(
                msg.caption or msg.text or "",
                msg.caption_entities if hasattr(msg, 'caption_entities') else msg.entities
            )
            caption = caption[:1024] if caption else None

        if msg.photo:
            if i == 0:
                media.append(InputMediaPhoto(media=msg.photo[-1].file_id, caption=caption))
            else:
                media.append(InputMediaPhoto(media=msg.photo[-1].file_id))
        elif msg.video:
            if i == 0:
                media.append(InputMediaVideo(media=msg.video.file_id, caption=caption))
            else:
                media.append(InputMediaVideo(media=msg.video.file_id))

    if media:
        sent = await bot.send_media_group(chat_id=target_chat_id, media=media)
        return [msg.message_id for msg in sent]
    return []

# Основной цикл обработки сообщений
async def main_loop():
    # Получаем ID канала-источника
    try:
        source_chat = await bot.get_chat(SOURCE_CHANNEL)
        source_chat_id = source_chat.id
        logger.info(f"Подписан на канал: {source_chat.title} (ID: {source_chat_id})")
    except Exception as e:
        logger.error(f"Не могу подписаться на {SOURCE_CHANNEL}: {e}")
        return

    # Получаем ID целевого канала
    try:
        target_chat = await bot.get_chat(TARGET_CHANNEL)
        target_chat_id = target_chat.id
        logger.info(f"Целевой канал: {target_chat.title} (ID: {target_chat_id})")
    except Exception as e:
        logger.error(f"Ошибка доступа к {TARGET_CHANNEL}: {e}")
        return

    logger.info(f"🚀 Бот запущен. Следит за {SOURCE_CHANNEL} -> {TARGET_CHANNEL}")

    last_update_id = 0
    album_buffer = {}  # Буфер для группировки альбомов

    while True:
        try:
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=30)

            for update in updates:
                last_update_id = update.update_id

                # Проверяем сообщения из канала-источника
                if update.channel_post:
                    msg = update.channel_post
                    if msg.chat_id != source_chat_id:
                        continue

                    # Пропускаем дубли
                    if is_posted(msg.message_id, source_chat_id):
                        continue

                    # Обработка альбомов (несколько фото)
                    if msg.media_group_id:
                        group_id = msg.media_group_id
                        if group_id not in album_buffer:
                            album_buffer[group_id] = []
                            # Ждём 3 секунды, чтобы собрать все части альбома
                            await asyncio.sleep(3)

                        album_buffer[group_id].append(msg)

                        # Если это последнее сообщение в альбоме (примерно)
                        if len(album_buffer[group_id]) >= 2:
                            continue

                    # Обработка накопленных альбомов
                    for gid in list(album_buffer.keys()):
                        if album_buffer[gid]:
                            msgs = sorted(album_buffer[gid], key=lambda x: x.message_id)
                            if not is_posted(msgs[0].message_id, source_chat_id):
                                try:
                                    sent_ids = await send_album_to_target(msgs, target_chat_id)
                                    save_posted(msgs[0].message_id, sent_ids[0] if sent_ids else 0, source_chat_id)
                                    logger.info(f"✅ Альбом отправлен: {len(msgs)} медиа")
                                except Exception as e:
                                    logger.error(f"Ошибка альбома: {e}")
                        del album_buffer[gid]

                    # Обычные сообщения (не альбомы)
                    if not msg.media_group_id:
                        try:
                            sent_id = await send_to_target(msg, target_chat_id)
                            save_posted(msg.message_id, sent_id, source_chat_id)
                            logger.info(f"✅ Пост отправлен: source_id={msg.message_id}")
                        except Exception as e:
                            logger.error(f"Ошибка поста: {e}")

        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            await asyncio.sleep(60)

async def main():
    await main_loop()

if __name__ == "__main__":
    logger.info("Запуск бота...")
    asyncio.run(main())
