import os
import re
import time
import asyncio
import requests
import json
import logging
import base64
import threading
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
TARGET_GROUP_ID = -1003991874844

MENTION_REPLACE = '@esen_baevich'

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_FILE = 'session.session'
SESSION_B64_FILE = 'session.b64'
SOURCE_CHANNEL = '@blvckrooom'

TOPIC_IDS = {
    "Ассортимент": 477,
    "Ralph Lauren": 423,
    "GUCCI": 426,
    "FENDI": 425,
    "ZIMMERMANN": 421,
}

def detect_topic(text):
    if not text:
        return "Ассортимент"
    text_lower = text.lower()
    if 'prada' in text_lower: return "Ассортимент"
    if 'ralph lauren' in text_lower or 'ralphlauren' in text_lower: return "Ralph Lauren"
    if 'gucci' in text_lower: return "GUCCI"
    if 'fendi' in text_lower: return "FENDI"
    if 'zimmermann' in text_lower: return "ZIMMERMANN"
    if 'hermes' in text_lower: return "Ассортимент"
    if 'chanel' in text_lower: return "Ассортимент"
    return "Ассортимент"

def replace_mentions(text):
    return re.sub(r'@\w+', MENTION_REPLACE, text)

class FakeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_fake_server():
    server = HTTPServer(("0.0.0.0", 10000), FakeHandler)
    logger.info("✅ Фейковый HTTP-сервер запущен на порту 10000")
    server.serve_forever()

async def get_channel_albums():
    if not os.path.exists(SESSION_B64_FILE):
        logger.error(f"❌ Файл {SESSION_B64_FILE} не найден!")
        return []

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
        logger.info("✅ Сессия загружена из .b64")
    except Exception as e:
        logger.error(f"❌ Ошибка декодирования: {e}")
        return []

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    logger.info("✅ Подключение через сессию установлено!")
    
    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
    except Exception as e:
        logger.error(f"❌ Не удалось получить канал: {e}")
        return []

    albums = []
    history = await client(GetHistoryRequest(
        peer=channel,
        limit=50,
        offset_date=0,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))
    
    i = 0
    while i < len(history.messages):
        current = history.messages[i]
        
        if not current.photo:
            i += 1
            continue
        
        album_msgs = [current]
        j = i + 1
        while j < len(history.messages):
            next_msg = history.messages[j]
            time_diff = abs(next_msg.date - current.date)
            if next_msg.photo and time_diff.total_seconds() < 5:
                album_msgs.append(next_msg)
                j += 1
            else:
                break
        
        if len(album_msgs) > 1:
            text = album_msgs[-1].message or ""
            unique_photo_paths = []
            for m in album_msgs:
                try:
                    path = await client.download_media(m, file=f"temp_{m.id}.jpg")
                    if path:
                        unique_photo_paths.append(path)
                except:
                    pass
            
            if unique_photo_paths:
                albums.append({
                    "text": text,
                    "photo_paths": unique_photo_paths
                })
                logger.info(f"📚 Найден альбом с {len(unique_photo_paths)} уникальными фото")
        
        i = j
    
    logger.info(f"✅ Загружено {len(albums)} альбомов")
    await client.disconnect()
    return albums

def cleanup_topic(topic_name):
    thread_id = TOPIC_IDS.get(topic_name, 1)
    url = f"https://api.telegram.org/bot{TOKEN}/getChatHistory"
    params = {
        "chat_id": TARGET_GROUP_ID,
        "limit": 10,
        "message_thread_id": thread_id
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("ok"):
            messages = data.get("result", {}).get("messages", [])
            for msg in messages:
                if msg.get("from", {}).get("is_bot"):
                    del_url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
                    del_payload = {
                        "chat_id": TARGET_GROUP_ID,
                        "message_id": msg["message_id"]
                    }
                    requests.post(del_url, data=del_payload)
                    logger.info(f"🗑️ Удалён старый пост (ID: {msg['message_id']})")
    except:
        pass

def send_album_to_topic(topic_name, text, photo_paths):
    thread_id = TOPIC_IDS.get(topic_name)
    if not thread_id:
        logger.warning(f"⚠️ Тема '{topic_name}' не найдена, отправляю в общий чат")
        thread_id = 1

    # 1. Сначала чистим тему от старых постов
    cleanup_topic(topic_name)

    # 2. Генерируем уникальный ID для альбома (Telegram склеит по нему)
    group_id = random.randint(1000000, 9999999)
    
    # 3. Отправляем каждое фото как отдельное сообщение, но с одинаковым group_id
    for i, path in enumerate(photo_paths):
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': open(path, 'rb')}
        data = {
            "chat_id": TARGET_GROUP_ID,
            "message_thread_id": thread_id,
        }
        # Добавляем подпись только к первому фото
        if i == 0:
            data["caption"] = f"📌 **{topic_name}**\n\n{text}"
            data["parse_mode"] = "Markdown"
        
        # Секретный ингредиент: media_group_id заставляет Telegram склеить фото
        if len(photo_paths) > 1:
            data["media_group_id"] = group_id
        
        try:
            requests.post(url, files=files, data=data, timeout=30)
            logger.info(f"📸 Отправлено фото {i+1}/{len(photo_paths)} в {topic_name}")
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"❌ Ошибка отправки фото {i+1}: {e}")

    logger.info(f"📚 Альбом ({len(photo_paths)} фото) отправлен в {topic_name} (ID: {thread_id})")

def main():
    logger.info("🚀 Запуск Супер-бота (альбомы с group_id)...")
    albums = asyncio.run(get_channel_albums())
    if not albums:
        logger.info("Альбомов не найдено.")
        return

    for album in albums:
        text = replace_mentions(album["text"])
        topic = detect_topic(text)
        photo_paths = album["photo_paths"]
        send_album_to_topic(topic, text, photo_paths)
        time.sleep(6)

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_fake_server, daemon=True)
    http_thread.start()
    main()
