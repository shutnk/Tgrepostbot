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

TOPIC_MAP = {
    "ralph lauren": "Ralph Lauren",
    "fendi": "FENDI",
    "gucci": "GUCCI",
    "zimmermann": "ZIMMERMANN",
    "сумки hermes": "Ассортимент",
    "обувь hermes": "Ассортимент",
    "ремень hermes": "Ремень Hermes",
    "сумки chanel": "Ассортимент",
    "chanel": "Ассортимент",
    "женская одежда": "Ассортимент",
    "сумки the row": "Ассортимент",
    "сумки miu miu": "Ассортимент",
    "одежда для детей": "Ассортимент",
    "сумки prada": "Ассортимент",
    "chrome hearts": "Ассортимент",
    "женская обувь": "Ассортимент",
    "сумки ysl": "Ассортимент",
    "женская верхняя одежда": "Ассортимент",
    "ремни": "Ассортимент",
    "шарфы и шапки": "Ассортимент",
    "очки": "Очки",
    "украшения schiaparelli": "Ассортимент",
    "сумки schiaparelli": "Ассортимент",
    "dolce&gabbana": "Ассортимент",
    "мужская верхняя одежда": "Ассортимент",
    "купальники": "Ассортимент",
    "сумки loewe": "Ассортимент",
    "сумки loro piana": "Ассортимент",
    "сумки bottega veneta": "Ассортимент",
    "классическая мужская обувь": "Ассортимент",
    "сумки louis vuitton": "Ассортимент",
    "exclusive": "Ассортимент",
    "balenciaga": "Ассортимент",
    "сумки jacquemus": "Ассортимент",
    "сумки balenciaga": "Ассортимент",
    "кроссовки louis vuitton": "Ассортимент",
    "кроссовки luxury": "Ассортимент",
    "сумки dior": "Ассортимент",
    "сумки goyard": "Ассортимент",
    "мужские сумки": "Ассортимент",
    "чемоданы": "Ассортимент",
    "сумки bvlgari": "Ассортимент",
    "сумки manolo blahnik": "Ассортимент",
    "обувь alaïa": "Ассортимент",
    "burberry": "Ассортимент",
    "moncler": "Ассортимент",
    "обвесы на сумку": "Ассортимент",
    "кроссовки balenciaga": "Ассортимент",
    "обувь chanel": "Ассортимент",
    "обувь для пляжа": "Ассортимент",
    "женские сапоги": "Ассортимент",
    "обувь loro piana": "Ассортимент",
    "acne studios": "Ассортимент",
    "chrome hearts украшения из серебра": "Ассортимент",
    "сумки chrome hearts": "Ассортимент",
    "товары для дома": "Ассортимент",
    "сумки celine": "Ассортимент",
    "лоферы loro piana": "Ассортимент",
    "сумки maison margiela": "Ассортимент",
    "сумки acne studios": "Ассортимент",
    "сумки lemaire": "Ассортимент",
    "украшения (бижутерия)": "Ассортимент",
    "canada goose": "Ассортимент",
    "yves saint laurent": "Ассортимент",
    "ami paris": "Ассортимент",
    "кроссовки loewe": "Ассортимент",
    "кроссовки gucci": "Ассортимент",
    "arcteryx": "Ассортимент",
    "givenchy": "Ассортимент",
    "классическая мужская одежда": "Ассортимент",
    "maison margiela": "Ассортимент",
    "welldone": "Ассортимент",
    "amiri": "Ассортимент",
    "женская обувь ii": "Ассортимент",
    "сумки roger vivier": "Ассортимент",
    "сумки dolce gabbana": "Ассортимент",
    "сумки alaïa": "Ассортимент",
    "зимние куртки": "Ассортимент",
    "обувь для детей": "Ассортимент",
    "экзотическая кожа": "Ассортимент",
    "сумки ralph lauren": "Ассортимент",
    "сумки mcm": "Ассортимент",
    "max mara": "Ассортимент",
    "пальто": "Ассортимент",
    "alexander wang": "Ассортимент",
    "enfants riches deprimes": "Ассортимент",
    "ювелирные украшения": "Ассортимент",
    "обувь louis vuitton": "Ассортимент",
    "сумки moynat paris": "Ассортимент",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_topic(text):
    if not text:
        return "Ассортимент"
    lower_text = text.lower()
    for keyword, topic in TOPIC_MAP.items():
        if keyword in lower_text:
            return topic
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

async def get_channel_posts():
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

    posts = []
    history = await client(GetHistoryRequest(
        peer=channel,
        limit=100,
        offset_date=0,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))
    for msg in reversed(history.messages):
        if msg.message or msg.media:
            text = msg.message or ""
            photo_urls = []
            if msg.media:
                # Если это медиа-группа, получаем все фото через группу
                if msg.grouped_id:
                    group_messages = await client.get_messages(channel, limit=10, min_id=msg.id - 5)
                    for g_msg in group_messages:
                        if g_msg.grouped_id == msg.grouped_id and g_msg.photo:
                            try:
                                photo_path = await client.download_media(g_msg, file="temp_photo.jpg")
                                photo_urls.append(photo_path)
                            except:
                                pass
                else:
                    try:
                        photo_path = await client.download_media(msg, file="temp_photo.jpg")
                        photo_urls.append(photo_path)
                    except:
                        pass
            posts.append({"text": text, "photo_urls": photo_urls})
    logger.info(f"✅ Загружено {len(posts)} постов из канала")
    await client.disconnect()
    return posts

def send_to_topic(topic_name, text, photo_url=None):
    thread_id = TOPIC_IDS.get(topic_name)
    
    if not thread_id:
        logger.warning(f"⚠️ Тема '{topic_name}' не в TOPIC_IDS, отправляю в общий чат")
        thread_id = 1

    async def send_telethon():
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.connect()
        if photo_url:
            await client.send_file(
                TARGET_GROUP_ID,
                file=photo_url,
                caption=f"📌 **{topic_name}**\n\n{text}",
                parse_mode="markdown",
                reply_to=thread_id
            )
        else:
            await client.send_message(
                TARGET_GROUP_ID,
                f"📌 **{topic_name}**\n\n{text}",
                reply_to=thread_id
            )
        await client.disconnect()
    
    try:
        asyncio.run(send_telethon())
        logger.info(f"📦 Отправлено через Telethon в {topic_name} (ID: {thread_id})")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки через Telethon: {e}")

def main():
    logger.info("🚀 Запуск финального копирования...")
    posts = asyncio.run(get_channel_posts())
    if not posts:
        logger.info("Постов не найдено.")
        return

    for post in posts:
        text = replace_mentions(post["text"])
        topic = detect_topic(text)
        for photo_url in post["photo_urls"]:
            send_to_topic(topic, text, photo_url)
            time.sleep(2)

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_fake_server, daemon=True)
    http_thread.start()
    main()
