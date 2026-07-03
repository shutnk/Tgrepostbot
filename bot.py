import os
import re
import time
import asyncio
import logging
import base64
import requests
from flask import Flask, jsonify
from telethon import TelegramClient, functions
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

TOPIC_IDS = {
    "Ассортимент": 477,
    "Ralph Lauren": 423,
    "GUCCI": 426,
    "FENDI": 425,
    "ZIMMERMANN": 421,
    "Сумки Hermes": 392,
    "Обувь Hermes": 394,
    "Ремень Hermes": 386,
    "Сумки CHANEL": 396,
    "Chanel": 399,
    "Женская одежда": 397,
    "Сумки THE ROW": 398,
    "Сумки MIU MIU": 400,
    "Одежда для детей": 401,
    "Сумки PRADA": 402,
    "CHROME HEARTS": 403,
    "Женская обувь": 404,
    "Сумки YSL": 405,
    "Женская верхняя одежда (Кожа, кашемир)": 406,
    "Ремни": 407,
    "Шарфы и шапки": 408,
    "Одежда Loro/Brunello/Kiton/Zegna": 409,
    "Очки": 410,
    "Украшения Schiaparelli": 411,
    "Сумки Schiaparelli": 412,
    "Dolce&Gabbana": 413,
    "Мужская верхняя одежда": 414,
    "Купальники и пляжная одежда": 415,
    "Сумки Loewe": 416,
    "Сумки Loro Piana": 417,
    "Сумки BOTTEGA VENETA": 418,
    "Классическая мужская обувь": 419,
    "Сумки Louis Vuitton": 420,
    "EXCLUSIVE": 422,
    "BALENCIAGA": 424,
    "Сумки Jacquemus": 427,
    "Сумки BALENCIAGA": 428,
    "Кроссовки Louis Vuitton": 429,
    "Кроссовки [LUXURY SNEAKERS]": 430,
    "Сумки DIOR": 431,
    "Сумки GOYARD": 432,
    "Мужские сумки": 433,
    "Чемоданы и дорожные сумки": 434,
    "Сумки BVLGARI": 435,
    "Сумки Manolo Blahnik": 436,
    "Обувь Alaïa": 437,
    "BURBERRY": 438,
    "Moncler": 439,
    "Обвесы на сумку": 440,
    "Кроссовки BALENCIAGA": 441,
    "Обувь Chanel": 442,
    "Обувь для пляжа и бассейна": 443,
    "Женские сапоги": 444,
    "Обувь Loro/Brunello/Kiton/Zegna": 445,
    "Acne Studios": 446,
    "CHROME HEARTS Украшения из серебра": 447,
    "Сумки Chrome Hearts": 448,
    "Товары для дома": 449,
    "Сумки CELINE": 450,
    "Лоферы Loro Piana": 451,
    "Сумки Maison Margiela": 452,
    "Сумки Acne Studios": 453,
    "Сумки LEMAIRE": 454,
    "Украшения (бижутерия)": 455,
    "CANADA GOOSE": 456,
    "Yves Saint Laurent": 457,
    "AMI Paris": 458,
    "Кроссовки LOEWE": 459,
    "Кроссовки GUCCI": 460,
    "Arcteryx": 461,
    "GIVENCHY": 462,
    "Классическая мужская одежда": 463,
    "MAISON MARGIELA": 464,
    "WELLDONE": 465,
    "AMIRI": 466,
    "Женская обувь II": 467,
    "Сумки Roger Vivier": 468,
    "Сумки Dolce Gabbana": 469,
    "Сумки Alaïa": 470,
    "Зимние куртки": 471,
    "Обувь для детей": 472,
    "Классическая мужская обувь из экзотической кожи": 473,
    "Сумки Ralph Lauren": 474,
    "Сумки MCM": 475,
    "Max Mara": 476,
    "Пальто": 478,
    "alexander wang": 479,
    "ENFANTS RICHES DEPRIMES": 480,
    "Ювелирные украшения": 481,
    "Обувь Louis Vuitton": 482,
    "Сумки MOYNAT PARIS": 483,
}

def detect_topic(text):
    if not text:
        return "Ассортимент"
    text_lower = text.lower()
    if 'prada' in text_lower: return "Сумки PRADA"
    if 'ralph lauren' in text_lower or 'ralphlauren' in text_lower: return "Ralph Lauren"
    if 'gucci' in text_lower: return "GUCCI"
    if 'fendi' in text_lower: return "FENDI"
    if 'zimmermann' in text_lower: return "ZIMMERMANN"
    if 'hermes' in text_lower: return "Сумки Hermes"
    if 'chanel' in text_lower: return "Chanel"
    if 'dior' in text_lower: return "Сумки DIOR"
    if 'louis vuitton' in text_lower: return "Сумки Louis Vuitton"
    if 'balenciaga' in text_lower: return "BALENCIAGA"
    if 'loewe' in text_lower: return "Сумки Loewe"
    if 'bottega veneta' in text_lower: return "Сумки BOTTEGA VENETA"
    if 'givenchy' in text_lower: return "GIVENCHY"
    if 'yves saint laurent' in text_lower: return "Yves Saint Laurent"
    if 'miu miu' in text_lower: return "Сумки MIU MIU"
    if 'the row' in text_lower: return "Сумки THE ROW"
    if 'zegna' in text_lower: return "Одежда Loro/Brunello/Kiton/Zegna"
    if 'loro piana' in text_lower: return "Сумки Loro Piana"
    if 'brunello cucinelli' in text_lower: return "Одежда Loro/Brunello/Kiton/Zegna"
    if 'acne studios' in text_lower: return "Acne Studios"
    if 'maison margiela' in text_lower: return "Сумки Maison Margiela"
    if 'lemaire' in text_lower: return "Сумки LEMAIRE"
    if 'celine' in text_lower: return "Сумки CELINE"
    if 'chrome hearts' in text_lower: return "CHROME HEARTS"
    if 'moncler' in text_lower: return "Moncler"
    if 'burberry' in text_lower: return "BURBERRY"
    if 'canada goose' in text_lower: return "CANADA GOOSE"
    if 'max mara' in text_lower: return "Max Mara"
    if 'mcm' in text_lower: return "Сумки MCM"
    if 'moynat' in text_lower: return "Сумки MOYNAT PARIS"
    if 'юбка' in text_lower: return "Женская одежда"
    if 'платье' in text_lower: return "Женская одежда"
    if 'брюки' in text_lower: return "Женская одежда"
    if 'шорты' in text_lower: return "Женская одежда"
    if 'футболка' in text_lower: return "Женская одежда"
    if 'рубашка' in text_lower: return "Женская одежда"
    if 'топ' in text_lower: return "Женская одежда"
    if 'куртка' in text_lower: return "Зимние куртки"
    if 'пальто' in text_lower: return "Пальто"
    if 'обувь' in text_lower: return "Женская обувь"
    if 'кроссовки' in text_lower: return "Кроссовки [LUXURY SNEAKERS]"
    if 'часы' in text_lower: return "Часы"
    if 'ремень' in text_lower: return "Ремни"
    if 'сумка' in text_lower: return "Ассортимент"
    if 'очки' in text_lower: return "Очки"
    if 'украшения' in text_lower: return "Ювелирные украшения"
    if 'шапка' in text_lower: return "Шарфы и шапки"
    if 'шарф' in text_lower: return "Шарфы и шапки"
    return "Ассортимент"

def replace_mentions(text):
    return re.sub(r'@\w+', MENTION_REPLACE, text)

async def process_albums(limit=100):
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
    # ИСПРАВЛЕННЫЙ ВЫЗОВ (позиционные аргументы для 1.44.0)
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

        thread_id = TOPIC_IDS.get(topic)
        if thread_id:
            url = f"https://api.telegram.org/bot{TOKEN}/getChatHistory"
            params = {"chat_id": TARGET_GROUP_ID, "limit": 10, "message_thread_id": thread_id}
            try:
                resp = requests.get(url, params=params, timeout=10)
                for msg in resp.json().get("result", {}).get("messages", []):
                    if msg.get("from", {}).get("is_bot"):
                        requests.post(
                            f"https://api.telegram.org/bot{TOKEN}/deleteMessage",
                            data={"chat_id": TARGET_GROUP_ID, "message_id": msg["message_id"]}
                        )
            except:
                pass

        if topic not in TOPIC_IDS:
            logger.info(f"🆕 Создаю тему: {topic}")
            client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
            await client.connect()
            group = await client.get_entity(TARGET_GROUP_ID)
            try:
                res = await client(functions.channels.CreateForumTopic(channel=group, title=topic))
                TOPIC_IDS[topic] = res.id
                logger.info(f"✅ Тема создана (ID: {res.id})")
            except Exception as e:
                logger.error(f"❌ Ошибка создания: {e}")
            await client.disconnect()

        thread_id = TOPIC_IDS.get(topic, 1)

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
