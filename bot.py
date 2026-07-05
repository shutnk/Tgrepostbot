import os
import re
import time
import asyncio
import logging
import base64
import requests
from flask import Flask, jsonify
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

app = Flask(__name__)

TOPIC_MAP = {
    "prada": "Сумки PRADA",
    "ralph lauren": "Ralph Lauren",
    "gucci": "GUCCI",
    "fendi": "FENDI",
    "zimmermann": "ZIMMERMANN",
    "hermes": "Сумки Hermes",
    "chanel": "Chanel",
    "dior": "Сумки DIOR",
    "louis vuitton": "Сумки Louis Vuitton",
    "balenciaga": "BALENCIAGA",
    "loewe": "Сумки Loewe",
    "bottega veneta": "Сумки BOTTEGA VENETA",
    "givenchy": "GIVENCHY",
    "yves saint laurent": "Yves Saint Laurent",
    "miu miu": "Сумки MIU MIU",
    "the row": "Сумки THE ROW",
    "zegna": "Одежда Loro/Brunello/Kiton/Zegna",
    "loro piana": "Сумки Loro Piana",
    "brunello cucinelli": "Одежда Loro/Brunello/Kiton/Zegna",
    "acne studios": "Acne Studios",
    "maison margiela": "Сумки Maison Margiela",
    "lemaire": "Сумки LEMAIRE",
    "celine": "Сумки CELINE",
    "chrome hearts": "CHROME HEARTS",
    "moncler": "Moncler",
    "burberry": "BURBERRY",
    "canada goose": "CANADA GOOSE",
    "max mara": "Max Mara",
    "mcm": "Сумки MCM",
    "moynat": "Сумки MOYNAT PARIS",
    "юбка": "Женская одежда",
    "платье": "Женская одежда",
    "брюки": "Женская одежда",
    "шорты": "Женская одежда",
    "футболка": "Женская одежда",
    "рубашка": "Женская одежда",
    "топ": "Женская одежда",
    "куртка": "Зимние куртки",
    "пальто": "Пальто",
    "обувь": "Обувь Hermes",
    "кроссовки": "Кроссовки [LUXURY SNEAKERS]",
    "часы": "Часы",
    "ремень": "Ремни",
    "сумка": "Ассортимент",
    "очки": "Очки",
    "украшения": "Ювелирные украшения",
    "шапка": "Шарфы и шапки",
    "шарф": "Шарфы и шапки",
}

def detect_topic(text):
    if not text:
        return "Ассортимент"
    text_lower = text.lower()
    if 'кроссовки' in text_lower: return "Кроссовки [LUXURY SNEAKERS]"
    if 'обувь' in text_lower: return "Обувь Hermes"
    if 'сумка' in text_lower: return "Сумки Hermes"
    for key, topic in TOPIC_MAP.items():
        if key in text_lower:
            return topic
    return "Ассортимент"

def replace_mentions(text):
    return re.sub(r'@\w+', MENTION_REPLACE, text)

async def get_topic_ids():
    if not os.path.exists(SESSION_B64_FILE):
        logger.error("❌ Нет сессии!")
        return {}

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки сессии: {e}")
        return {}

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    try:
        group = await client.get_entity(TARGET_GROUP_ID)
        # === Единственный рабочий способ в 1.44.0 ===
        participants = await client.get_participants(group)
        topic_ids = {}
        for p in participants:
            if hasattr(p, 'topic_id') and p.topic_id:
                # Имя темы берём из имени участника
                topic_name = p.first_name or p.title or f"Topic {p.topic_id}"
                topic_ids[topic_name] = p.topic_id
        logger.info(f"✅ Загружено {len(topic_ids)} тем через get_participants")
        await client.disconnect()
        return topic_ids
    except Exception as e:
        logger.error(f"❌ Ошибка получения тем: {e}")
        await client.disconnect()
        return {}

async def process_albums(limit=100):
    topic_ids = await get_topic_ids()
    if not topic_ids:
        logger.error("❌ Не удалось загрузить ID тем")
        return False

    if not os.path.exists(SESSION_B64_FILE):
        logger.error("❌ Нет сессии!")
        return False

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки сессии: {e}")
        return False

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    logger.info("✅ Подключено к аккаунту")

    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
    except Exception as e:
        logger.error(f"❌ Не удалось получить канал: {e}")
        await client.disconnect()
        return False

    albums = []
    history = await client(GetHistoryRequest(
        peer=channel,
        offset_id=0,
        offset_date=0,
        add_offset=0,
        max_id=0,
        min_id=0,
        hash=0,
        limit=limit
    ))
    
    i = 0
    while i < len(history.messages):
        msg = history.messages[i]
        if not msg.photo:
            i += 1
            continue
        group = [msg]
        j = i + 1
        while j < len(history.messages):
            nxt = history.messages[j]
            if nxt.photo and abs(nxt.date - msg.date).total_seconds() < 5:
                group.append(nxt)
                j += 1
            else:
                break
        if len(group) > 1:
            text = group[-1].message or ""
            photo_paths = set()
            for m in group:
                try:
                    p = await client.download_media(m, file=f"temp_{m.id}.jpg")
                    if p:
                        photo_paths.add(p)
                except:
                    pass
            if photo_paths:
                albums.append({"text": text, "photo_paths": list(photo_paths)})
        i = j

    await client.disconnect()
    logger.info(f"📚 Найдено {len(albums)} альбомов")

    if not albums:
        return True

    total_sent = 0
    for album in albums:
        text = replace_mentions(album["text"])
        topic = detect_topic(text)
        photos = album["photo_paths"]

        thread_id = topic_ids.get(topic)
        if not thread_id:
            logger.warning(f"⚠️ Тема '{topic}' не найдена, пытаюсь создать...")
            client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
            await client.connect()
            group = await client.get_entity(TARGET_GROUP_ID)
            try:
                # Создаём тему через аккаунт
                create_result = await client(functions.channels.CreateForumTopic(
                    channel=group,
                    title=topic
                ))
                thread_id = create_result.id
                topic_ids[topic] = thread_id
                logger.info(f"✅ Тема '{topic}' создана (ID: {thread_id})")
            except Exception as e:
                logger.error(f"❌ Ошибка создания темы {topic}: {e}")
            await client.disconnect()

        if thread_id:
            client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
            await client.connect()
            if photos:
                await client.send_file(
                    TARGET_GROUP_ID,
                    file=photos,
                    caption=f"📌 **{topic}**\n\n{text}",
                    parse_mode="markdown",
                    message_thread_id=thread_id,
                    album=True
                )
            await client.disconnect()
            logger.info(f"📚 Альбом ({len(photos)} фото) в {topic} (ID: {thread_id})")
            total_sent += 1
            time.sleep(3)

    logger.info(f"✅ Обработано {total_sent} альбомов")
    return True

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/health")
def health():
    asyncio.run(process_albums(limit=100))
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    asyncio.run(process_albums(limit=100))
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
