import os
import re
import time
import asyncio
import requests
import logging
import base64
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

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
    
    hashtags = re.findall(r'#(\w+)', text.lower())
    
    if 'prada' in hashtags:
        return "Ассортимент"
    if 'ralph lauren' in hashtags or 'ralphlauren' in hashtags:
        return "Ralph Lauren"
    if 'gucci' in hashtags:
        return "GUCCI"
    if 'fendi' in hashtags:
        return "FENDI"
    if 'zimmermann' in hashtags:
        return "ZIMMERMANN"
    if 'hermes' in hashtags:
        return "Ассортимент"
    if 'chanel' in hashtags:
        return "Ассортимент"
    
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
    
    grouped = {}
    for msg in history.messages:
        if msg.grouped_id:
            if msg.grouped_id not in grouped:
                grouped[msg.grouped_id] = []
            grouped[msg.grouped_id].append(msg)
    
    for group_id, messages in grouped.items():
        text = messages[-1].message or ""
        photo_urls = []
        for m in messages:
            if m.photo or m.document:
                if m.photo:
                    photo_urls.append(m.photo)
                elif m.document:
                    photo_urls.append(m.document)
        
        unique_photos = []
        seen = set()
        for p in photo_urls:
            if hasattr(p, 'file_id'):
                if p.file_id not in seen:
                    seen.add(p.file_id)
                    unique_photos.append(p)
            elif hasattr(p, 'id'):
                if p.id not in seen:
                    seen.add(p.id)
                    unique_photos.append(p)
        
        if unique_photos:
            albums.append({
                "text": text,
                "photos": unique_photos
            })
            logger.info(f"📚 Найден альбом с {len(unique_photos)} уникальными фото")
    
    logger.info(f"✅ Загружено {len(albums)} альбомов")
    await client.disconnect()
    return albums

def cleanup_old_duplicates(topic_name, new_text):
    """Удаляет старые сообщения бота в этой теме, похожие на новое"""
    thread_id = TOPIC_IDS.get(topic_name, 1)
    
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getChatHistory"
        payload = {
            "chat_id": TARGET_GROUP_ID,
            "limit": 10,
            "message_thread_id": thread_id
        }
        resp = requests.get(url, params=payload, timeout=10)
        data = resp.json()
        
        if not data.get("ok"):
            return
        
        messages = data.get("result", {}).get("messages", [])
        for msg in messages:
            # Проверяем, что сообщение от бота
            if msg.get("from", {}).get("is_bot"):
                # Если текст похож или есть фото
                if "caption" in msg and new_text in msg["caption"]:
                    # Удаляем
                    del_url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
                    del_payload = {
                        "chat_id": TARGET_GROUP_ID,
                        "message_id": msg["message_id"]
                    }
                    requests.post(del_url, data=del_payload)
                    logger.info(f"🗑️ Удалён старый дубликат (ID: {msg['message_id']})")
    except Exception as e:
        logger.error(f"❌ Ошибка очистки дубликатов: {e}")

def send_album_to_topic(topic_name, text, photos):
    thread_id = TOPIC_IDS.get(topic_name)
    if not thread_id:
        logger.warning(f"⚠️ Тема '{topic_name}' не найдена, отправляю в общий чат")
        thread_id = 1

    # Сначала удаляем старые дубликаты
    cleanup_old_duplicates(topic_name, text)

    url = f"https://api.telegram.org/bot{TOKEN}/sendMediaGroup"
    
    media = []
    for i, photo in enumerate(photos):
        file_id = None
        if hasattr(photo, 'file_id'):
            file_id = photo.file_id
        elif hasattr(photo, 'id'):
            file_id = photo.id
        
        if file_id:
            media_item = {"type": "photo", "media": file_id}
            if i == 0:
                media_item["caption"] = f"📌 **{topic_name}**\n\n{text}"
                media_item["parse_mode"] = "Markdown"
            media.append(media_item)
    
    if media:
        payload = {
            "chat_id": TARGET_GROUP_ID,
            "media": media,
            "message_thread_id": thread_id
        }
        try:
            requests.post(url, json=payload, timeout=15)
            logger.info(f"📚 Альбом ({len(media)} фото) отправлен в {topic_name} (ID: {thread_id})")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки альбома: {e}")

def main():
    logger.info("🚀 Запуск финального копирования (с очисткой дубликатов)...")
    albums = asyncio.run(get_channel_albums())
    if not albums:
        logger.info("Альбомов не найдено.")
        return

    for album in albums:
        text = replace_mentions(album["text"])
        topic = detect_topic(text)
        photos = album["photos"]
        send_album_to_topic(topic, text, photos)
        time.sleep(6)

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_fake_server, daemon=True)
    http_thread.start()
    main()
