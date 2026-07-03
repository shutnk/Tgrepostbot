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

# === НАСТРОЙКИ ===
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
    "Ассортимент": 477, "Ralph Lauren": 423, "GUCCI": 426, "FENDI": 425, "ZIMMERMANN": 421,
    "Сумки Hermes": 392, "Обувь Hermes": 394, "Ремень Hermes": 386, "Сумки CHANEL": 396,
    "Chanel": 399, "Женская одежда": 397, "Сумки THE ROW": 398, "Сумки MIU MIU": 400,
    "Одежда для детей": 401, "Сумки PRADA": 402, "CHROME HEARTS": 403, "Женская обувь": 404,
    "Сумки YSL": 405, "Женская верхняя одежда (Кожа, кашемир)": 406, "Ремни": 407,
    "Шарфы и шапки": 408, "Одежда Loro/Brunello/Kiton/Zegna": 409, "Очки": 410,
    "Украшения Schiaparelli": 411, "Сумки Schiaparelli": 412, "Dolce&Gabbana": 413,
    "Мужская верхняя одежда": 414, "Купальники и пляжная одежда": 415, "Сумки Loewe": 416,
    "Сумки Loro Piana": 417, "Сумки BOTTEGA VENETA": 418, "Классическая мужская обувь": 419,
    "Сумки Louis Vuitton": 420, "EXCLUSIVE": 422, "BALENCIAGA": 424, "Сумки Jacquemus": 427,
    "Сумки BALENCIAGA": 428, "Кроссовки Louis Vuitton": 429, "Кроссовки [LUXURY SNEAKERS]": 430,
    "Сумки DIOR": 431, "Сумки GOYARD": 432, "Мужские сумки": 433, "Чемоданы и дорожные сумки": 434,
    "Сумки BVLGARI": 435, "Сумки Manolo Blahnik": 436, "Обувь Alaïa": 437, "BURBERRY": 438,
    "Moncler": 439, "Обвесы на сумку": 440, "Кроссовки BALENCIAGA": 441, "Обувь Chanel": 442,
    "Обувь для пляжа и бассейна": 443, "Женские сапоги": 444, "Обувь Loro/Brunello/Kiton/Zegna": 445,
    "Acne Studios": 446, "CHROME HEARTS Украшения из серебра": 447, "Сумки Chrome Hearts": 448,
    "Товары для дома": 449, "Сумки CELINE": 450, "Лоферы Loro Piana": 451, "Сумки Maison Margiela": 452,
    "Сумки Acne Studios": 453, "Сумки LEMAIRE": 454, "Украшения (бижутерия)": 455,
    "CANADA GOOSE": 456, "Yves Saint Laurent": 457, "AMI Paris": 458, "Кроссовки LOEWE": 459,
    "Кроссовки GUCCI": 460, "Arcteryx": 461, "GIVENCHY": 462, "Классическая мужская одежда": 463,
    "MAISON MARGIELA": 464, "WELLDONE": 465, "AMIRI": 466, "Женская обувь II": 467,
    "Сумки Roger Vivier": 468, "Сумки Dolce Gabbana": 469, "Сумки Alaïa": 470, "Зимние куртки": 471,
    "Обувь для детей": 472, "Классическая мужская обувь из экзотической кожи": 473,
    "Сумки Ralph Lauren": 474, "Сумки MCM": 475, "Max Mara": 476, "Пальто": 478,
    "alexander wang": 479, "ENFANTS RICHES DEPRIMES": 480, "Ювелирные украшения": 481,
    "Обувь Louis Vuitton": 482, "Сумки MOYNAT PARIS": 483,
}

def detect_topic(text):
    if not text: return "Ассортимент"
    t = text.lower()
    if 'prada' in t: return "Сумки PRADA"
    if 'ralph lauren' in t or 'ralphlauren' in t: return "Ralph Lauren"
    if 'gucci' in t: return "GUCCI"
    if 'fendi' in t: return "FENDI"
    if 'zimmermann' in t: return "ZIMMERMANN"
    if 'hermes' in t: return "Сумки Hermes"
    if 'chanel' in t: return "Chanel"
    if 'dior' in t: return "Сумки DIOR"
    if 'louis vuitton' in t: return "Сумки Louis Vuitton"
    if 'balenciaga' in t: return "BALENCIAGA"
    if 'loewe' in t: return "Сумки Loewe"
    if 'bottega veneta' in t: return "Сумки BOTTEGA VENETA"
    if 'givenchy' in t: return "GIVENCHY"
    if 'yves saint laurent' in t: return "Yves Saint Laurent"
    if 'miu miu' in t: return "Сумки MIU MIU"
    if 'the row' in t: return "Сумки THE ROW"
    if 'zegna' in t: return "Одежда Loro/Brunello/Kiton/Zegna"
    if 'loro piana' in t: return "Сумки Loro Piana"
    if 'brunello cucinelli' in t: return "Одежда Loro/Brunello/Kiton/Zegna"
    if 'acne studios' in t: return "Acne Studios"
    if 'maison margiela' in t: return "Сумки Maison Margiela"
    if 'lemaire' in t: return "Сумки LEMAIRE"
    if 'celine' in t: return "Сумки CELINE"
    if 'chrome hearts' in t: return "CHROME HEARTS"
    if 'moncler' in t: return "Moncler"
    if 'burberry' in t: return "BURBERRY"
    if 'canada goose' in t: return "CANADA GOOSE"
    if 'max mara' in t: return "Max Mara"
    if 'mcm' in t: return "Сумки MCM"
    if 'moynat' in t: return "Сумки MOYNAT PARIS"
    if 'юбка' in t: return "Женская одежда"
    if 'платье' in t: return "Женская одежда"
    if 'брюки' in t: return "Женская одежда"
    if 'шорты' in t: return "Женская одежда"
    if 'футболка' in t: return "Женская одежда"
    if 'рубашка' in t: return "Женская одежда"
    if 'топ' in t: return "Женская одежда"
    if 'куртка' in t: return "Зимние куртки"
    if 'пальто' in t: return "Пальто"
    if 'обувь' in t: return "Женская обувь"
    if 'кроссовки' in t: return "Кроссовки [LUXURY SNEAKERS]"
    if 'часы' in t: return "Часы"
    if 'ремень' in t: return "Ремни"
    if 'сумка' in t: return "Ассортимент"
    if 'очки' in t: return "Очки"
    if 'украшения' in t: return "Ювелирные украшения"
    if 'шапка' in t: return "Шарфы и шапки"
    if 'шарф' in t: return "Шарфы и шапки"
    return "Ассортимент"

def replace_mentions(text):
    return re.sub(r'@\w+', MENTION_REPLACE, text)

async def get_channel_albums():
    if not os.path.exists(SESSION_B64_FILE):
        return []
    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except:
        return []

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
    except:
        await client.disconnect()
        return []

    albums = []
    history = await client(GetHistoryRequest(peer=channel, limit=10))
    i = 0
    while i < len(history.messages):
        current = history.messages[i]
        if not current.photo:
            i += 1
            continue
        album_msgs = [current]
        j = i + 1
        while j < len(history.messages):
            nxt = history.messages[j]
            if nxt.photo and abs(nxt.date - current.date).total_seconds() < 5:
                album_msgs.append(nxt)
                j += 1
            else:
                break
        if len(album_msgs) > 1:
            text = album_msgs[-1].message or ""
            photo_paths = []
            for m in album_msgs:
                try:
                    p = await client.download_media(m, file=f"temp_{m.id}.jpg")
                    if p: photo_paths.append(p)
                except: pass
            if photo_paths:
                albums.append({"text": text, "photo_paths": photo_paths})
        i = j
    await client.disconnect()
    return albums

async def ensure_topic_exists(topic_name):
    if topic_name in TOPIC_IDS: return TOPIC_IDS[topic_name]
    logger.info(f"🆕 Создаю тему: {topic_name}")
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    group = await client.get_entity(TARGET_GROUP_ID)
    try:
        res = await client(functions.channels.CreateForumTopic(channel=group, title=topic_name))
        new_id = res.id
        TOPIC_IDS[topic_name] = new_id
        logger.info(f"✅ Тема создана (ID: {new_id})")
    except Exception as e:
        logger.error(f"❌ Ошибка создания: {e}")
    await client.disconnect()
    return TOPIC_IDS.get(topic_name)

async def clear_topic_messages(topic_name):
    thread_id = TOPIC_IDS.get(topic_name)
    if not thread_id: return
    url = f"https://api.telegram.org/bot{TOKEN}/getChatHistory"
    params = {"chat_id": TARGET_GROUP_ID, "limit": 20, "message_thread_id": thread_id}
    try:
        resp = requests.get(url, params=params, timeout=10)
        for msg in resp.json().get("result", {}).get("messages", []):
            if msg.get("from", {}).get("is_bot"):
                requests.post(f"https://api.telegram.org/bot{TOKEN}/deleteMessage",
                              data={"chat_id": TARGET_GROUP_ID, "message_id": msg["message_id"]})
    except: pass

async def send_album():
    albums = await get_channel_albums()
    if not albums: return False
    album = albums[0]
    text = replace_mentions(album["text"])
    topic = detect_topic(text)
    photo_paths = album["photo_paths"]
    await clear_topic_messages(topic)
    thread_id = await ensure_topic_exists(topic)
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    if photo_paths:
        await client.send_file(TARGET_GROUP_ID, file=photo_paths,
                               caption=f"📌 **{topic}**\n\n{text}",
                               parse_mode="markdown", message_thread_id=thread_id, album=True)
    await client.disconnect()
    logger.info(f"📚 Альбом ({len(photo_paths)} фото) в {topic}")
    return True

@app.route("/")
def index():
    return jsonify({"status": "ok", "bot": "running"})

@app.route("/health")
def health():
    # Запускаем обработку при каждом пинге
    asyncio.run(send_album())
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
