import os
import re
import asyncio
import logging
import base64
import json
import random
from flask import Flask, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest

# ===== НАСТРОЙКИ =====
API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_B64_FILE = 'session.b64'
SOURCE_CHANNEL = '@blvckrooom'
TARGET_GROUP_ID = -1003991874844  # @trifferi_katalog
MENTION_REPLACE = '@esen_baevich'
ADMIN_ID = 5468112563

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# ===== СПИСОК ВСЕХ ТЕМ =====
ALL_TOPICS = [
    "Arcteryx", "GIVENCHY", "Классическая мужская одежда", "MAISON MARGIELA",
    "WELLDONE", "AMIRI", "Женская обувь II", "Сумки Roger Vivier",
    "Сумки Dolce Gabbana", "Сумки Alaïa", "Зимние куртки", "Обувь для детей",
    "Сумки Ralph Lauren", "Сумки MCM", "Ассортимент", "Пальто",
    "ENFANTS RICHES DEPRIMES", "Ювелирные украшения", "Обувь Louis Vuitton",
    "Сумки MOYNAT PARIS", "Сумки CELINE", "Лоферы Loro Piana",
    "Сумки Maison Margiela", "CELINE", "Сумки Acne Studios", "MIU MIU",
    "Сумки LEMAIRE", "CANADA GOOSE", "Yves Saint Laurent", "AMI Paris",
    "Кроссовки LOEWE", "Кроссовки GUCCI", "Чемоданы и дорожные сумки",
    "Сумки BVLGARI", "Сумки Manolo Blahnik", "Обувь Alaïa", "BURBERRY",
    "Moncler", "Обвесы на сумку", "Обувь для пляжа и бассейна",
    "CHROME HEARTS Украшения из серебра", "Сумки Chrome Hearts", "Товары для дома",
    "Сумки MIU MIU", "Сумки YSL", "Ремни", "Dolce&Gabbana",
    "Купальники и пляжная одежда", "Loewe", "BALENCIAGA", "FENDI",
    "GUCCI", "Сумки Jacquemus", "Сумки GOYARD", "Ralph Lauren", "HERMES",
    "BOTTEGA VENETA", "Одежда для детей", "Кроссовки [LUXURY SNEAKERS]",
    "Женские сапоги", "Очки", "Украшения(бижутерия)", "Кроссовки BALENCIAGA",
    "Классическая мужская обувь", "Кроссовки Louis Vuitton", "CHROME HEARTS",
    "Классическая мужская обувь из экзотической кожи", "Женская обувь",
    "Женская верхняя одежда(Кожа,кашемир)", "Max Mara", "Украшения Schiaparelli",
    "Сумки Schiaparelli", "Мужская верхняя одежда", "Обувь Chanel",
    "Acne Studios", "Chanel", "Обувь Loro/Brunello/Kiton/Zegna",
    "ZIMMERMANN", "Сумки THE ROW", "Сумки BALENCIAGA", "Сумки Louis Vuitton",
    "Мужские Сумки", "Сумки DIOR", "Сумки Loro Piana", "Сумки BOTTEGA VENETA",
    "Сумки PRADA", "Шарфы и шапки", "Часы", "Сумки Hermes", "Обувь Hermes",
    "Ремень Hermes", "EXCLUSIVE", "DIOR", "PRADA", "Louis Vuitton",
    "Сумки CHANEL", "Сумки Loewe", "Женская одежда",
    "Одежда Loro/Brunello/Kiton/Zegna"
]

# ===== ЗАГРУЗКА СЕССИИ (исправленная версия) =====
def load_session():
    if not os.path.exists(SESSION_B64_FILE):
        logger.error("❌ Нет сессии!")
        return None

    try:
        # Читаем файл как бинарный, декодируем в строку UTF-8
        with open(SESSION_B64_FILE, 'rb') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data).decode('utf-8')
        return StringSession(decoded)
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки сессии: {e}")
        return None

# ===== СОЗДАНИЕ ТЕМЫ (RAW API через _call) =====
async def create_topic(client, group, topic_name):
    try:
        result = await client._call(
            'channels.createForumTopic',
            {
                'channel': await client.get_input_entity(group),
                'title': topic_name
            }
        )
        logger.info(f"✅ Создана тема: {topic_name} (ID: {result.id})")
        return result.id
    except Exception as e:
        logger.error(f"❌ Ошибка создания темы {topic_name}: {e}")
        return None

# ===== ПОЛУЧЕНИЕ ТЕМ =====
async def get_topic_ids(client, group):
    try:
        dialogs = await client.get_dialogs()
        topics = {}
        for dialog in dialogs:
            if dialog.entity.id == TARGET_GROUP_ID and hasattr(dialog, 'forum_topics'):
                if dialog.forum_topics:
                    for topic in dialog.forum_topics:
                        topics[topic.title] = topic.id
                    break
        return topics
    except Exception as e:
        logger.error(f"❌ Ошибка получения тем: {e}")
        return {}

# ===== ОСНОВНОЙ БОТ =====
async def process_albums(limit=100):
    logger.info("🚀 Запуск от имени @nurikadambol...")

    session = load_session()
    if not session:
        return False

    client = TelegramClient(session, API_ID, API_HASH)
    await client.connect()

    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
        logger.info(f"✅ Канал {SOURCE_CHANNEL} найден")
    except Exception as e:
        logger.error(f"❌ Ошибка канала: {e}")
        await client.disconnect()
        return False

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

    albums = []
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

    logger.info(f"📚 Найдено {len(albums)} альбомов")

    group = await client.get_entity(TARGET_GROUP_ID)

    # Сначала создаём все темы из списка
    logger.info("🛠️ Начинаю создание всех тем...")
    for topic_name in ALL_TOPICS:
        logger.info(f"🛠️ Проверяю тему: {topic_name}")
        await create_topic(client, group, topic_name)
        await asyncio.sleep(0.5)

    # После создания — получаем список тем
    topic_ids = await get_topic_ids(client, group)
    logger.info(f"📋 Найдено {len(topic_ids)} тем")

    total_sent = 0
    for idx, album in enumerate(albums):
        text = replace_mentions(album["text"])
        topic = detect_topic(text)
        photos = album["photo_paths"]
        thread_id = topic_ids.get(topic)

        if not thread_id:
            logger.warning(f"⚠️ Тема '{topic}' не найдена. Отправляю в General.")
            thread_id = None

        for attempt in range(3):
            try:
                caption = f"📌 **{topic}**\n\n{text}" if text else None
                await client.send_file(
                    entity=group,
                    file=photos,
                    caption=caption,
                    parse_mode="markdown",
                    message_thread_id=thread_id
                )
                logger.info(f"✅ Отправлен альбом #{idx+1} в {topic if thread_id else 'General'}")
                total_sent += 1
                break
            except Exception as e:
                logger.error(f"❌ Попытка {attempt+1}: {e}")
                await asyncio.sleep(2)

    await client.disconnect()
    logger.info(f"🎉 Отправлено {total_sent} альбомов.")
    return True

# ===== ОПРЕДЕЛЕНИЕ ТЕМЫ =====
def detect_topic(text):
    TOPIC_MAP = {
        "обувь hermes": "Обувь Hermes",
        "обувь chanel": "Обувь Chanel",
        "обувь alaïa": "Обувь Alaïa",
        "обувь loro piana": "Лоферы Loro Piana",
        "обувь louis vuitton": "Обувь Louis Vuitton",
        "женские сапоги": "Женские сапоги",
        "женская обувь": "Женская обувь",
        "классическая мужская обувь": "Классическая мужская обувь",
        "кроссовки": "Кроссовки [LUXURY SNEAKERS]",
        "сумки hermes": "Сумки Hermes",
        "сумки chanel": "Сумки CHANEL",
        "сумки dior": "Сумки DIOR",
        "сумки louis vuitton": "Сумки Louis Vuitton",
        "сумки balenciaga": "Сумки BALENCIAGA",
        "сумки prada": "Сумки PRADA",
        "сумки goyard": "Сумки GOYARD",
        "сумки loewe": "Сумки Loewe",
        "сумки bottega veneta": "Сумки BOTTEGA VENETA",
        "сумки celine": "Сумки CELINE",
        "сумки fendi": "Сумки FENDI",
        "сумки miu miu": "Сумки MIU MIU",
        "сумки the row": "Сумки THE ROW",
        "сумки ralph lauren": "Сумки Ralph Lauren",
        "сумки mcm": "Сумки MCM",
        "сумки moynat paris": "Сумки MOYNAT PARIS",
        "сумки acne studios": "Сумки Acne Studios",
        "сумки lemaire": "Сумки LEMAIRE",
        "сумки maison margiela": "Сумки Maison Margiela",
        "сумки chroma hearts": "Сумки Chrome Hearts",
        "сумки jacquemus": "Сумки Jacquemus",
        "сумки bulgari": "Сумки BVLGARI",
        "сумки manolo blahnik": "Сумки Manolo Blahnik",
        "сумки roger vivier": "Сумки Roger Vivier",
        "сумки dolce gabbana": "Сумки Dolce Gabbana",
        "сумки alaïa": "Сумки Alaïa",
        "сумки schiaparelli": "Сумки Schiaparelli",
        "мужские сумки": "Мужские Сумки",
        "чемоданы и дорожные сумки": "Чемоданы и дорожные сумки",
        "обвесы на сумку": "Обвесы на сумку",
        "сумка": "Сумки Hermes",
        "женская одежда": "Женская одежда",
        "женская верхняя одежда": "Женская верхняя одежда(Кожа,кашемир)",
        "мужская верхняя одежда": "Мужская верхняя одежда",
        "зимние куртки": "Зимние куртки",
        "пальто": "Пальто",
        "arc'teryx": "Arcteryx",
        "canada goose": "CANADA GOOSE",
        "moncler": "Moncler",
        "burberry": "BURBERRY",
        "max mara": "Max Mara",
        "zegna": "Одежда Loro/Brunello/Kiton/Zegna",
        "loro piana": "Одежда Loro/Brunello/Kiton/Zegna",
        "brunello cucinelli": "Одежда Loro/Brunello/Kiton/Zegna",
        "kiton": "Одежда Loro/Brunello/Kiton/Zegna",
        "одежда для детей": "Одежда для детей",
        "купальники и пляжная одежда": "Купальники и пляжная одежда",
        "часы": "Часы",
        "ремень hermes": "Ремень Hermes",
        "ремни": "Ремни",
        "очки": "Очки",
        "украшения": "Ювелирные украшения",
        "украшения(бижутерия)": "Украшения(бижутерия)",
        "украшения schiaparelli": "Украшения Schiaparelli",
        "chrome hearts украшения": "CHROME HEARTS Украшения из серебра",
        "шарфы и шапки": "Шарфы и шапки",
        "товары для дома": "Товары для дома",
        "hermes": "HERMES",
        "chanel": "Chanel",
        "dior": "DIOR",
        "louis vuitton": "Louis Vuitton",
        "prada": "PRADA",
        "gucci": "GUCCI",
        "fendi": "FENDI",
        "balenciaga": "BALENCIAGA",
        "loewe": "Loewe",
        "bottega veneta": "BOTTEGA VENETA",
        "celine": "CELINE",
        "givenchy": "GIVENCHY",
        "ysl": "Yves Saint Laurent",
        "yves saint laurent": "Yves Saint Laurent",
        "miu miu": "MIU MIU",
        "the row": "THE ROW",
        "ralph lauren": "Ralph Lauren",
        "mcm": "MCM",
        "acne studios": "Acne Studios",
        "maison margiela": "MAISON MARGIELA",
        "chrome hearts": "CHROME HEARTS",
        "jacquemus": "Jacquemus",
        "moncler": "Moncler",
        "burberry": "BURBERRY",
        "canada goose": "CANADA GOOSE",
        "arc'teryx": "Arcteryx",
        "max mara": "Max Mara",
        "well done": "WELLDONE",
        "welldone": "WELLDONE",
        "ami paris": "AMI Paris",
        "alexander wang": "alexander wang",
        "enfants riches deprimes": "ENFANTS RICHES DEPRIMES",
        "dolce gabbana": "Dolce&Gabbana",
        "dolce&gabbana": "Dolce&Gabbana",
        "schiaparelli": "Schiaparelli",
        "exclusive": "EXCLUSIVE",
        "assortiment": "Ассортимент",
        "ассортимент": "Ассортимент",
    }
    if not text:
        return "Ассортимент"
    text_lower = text.lower()
    for key, topic in TOPIC_MAP.items():
        if key in text_lower:
            return topic
    return "Ассортимент"

def replace_mentions(text):
    return re.sub(r'@\w+', MENTION_REPLACE, text)

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
