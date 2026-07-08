import os
import re
import asyncio
import logging
import base64
import json
import traceback
import sys
import random
from flask import Flask, jsonify
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest, SendMessageRequest

# ===== НАСТРОЙКИ =====
API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_FILE = 'session.session'
SESSION_B64_FILE = 'session.b64'
SOURCE_CHANNEL = '@blvckrooom'
TARGET_GROUP_ID = -1003991874844  # @trifferi_katalog
MENTION_REPLACE = '@esen_baevich'

ADMIN_ID = 5468112563

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# ===== СПИСОК ТЕМ =====
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

# ===== ЛОГГЕР =====
class AILogger:
    def __init__(self, client=None):
        self.client = client
        self.error_count = 0
        self.max_errors = 3

    async def send_report(self, message, level="INFO"):
        if not self.client:
            return
        try:
            await self.client.send_message(ADMIN_ID, f"🤖 **{level}**\n{message}")
        except:
            pass

    async def log_step(self, step_name, details, success=True):
        emoji = "✅" if success else "❌"
        msg = f"{emoji} **{step_name}**\n{details}"
        logger.info(msg)
        await self.send_report(msg, "STEP")

    async def log_error(self, error, context="", solution_hint=""):
        self.error_count += 1
        msg = f"❌ **ОШИБКА #{self.error_count}**\nКонтекст: {context}\nОшибка: {error}\n"
        if solution_hint:
            msg += f"💡 **Предлагаю:** {solution_hint}"
        logger.error(msg)
        await self.send_report(msg, "ERROR")

        if self.error_count >= self.max_errors:
            await self.send_report("🚨 **Достигнут лимит ошибок. Бот завершает работу.**", "CRITICAL")
            logger.critical("Достигнут лимит ошибок. Завершение работы.")
            sys.exit(1)

# ===== СОЗДАНИЕ ВСЕХ ТЕМ =====
async def create_all_topics():
    logger.info("🚀 Запуск менеджера тем: создаю темы из списка...")
    
    if not os.path.exists(SESSION_B64_FILE):
        logger.error("❌ Нет сессии!")
        return

    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки сессии: {e}")
        return

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    try:
        group = await client.get_entity(TARGET_GROUP_ID)
        
        existing_topics = set()
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            if dialog.entity.id == TARGET_GROUP_ID and hasattr(dialog, 'forum_topics'):
                if dialog.forum_topics:
                    for topic in dialog.forum_topics:
                        existing_topics.add(topic.title)
                    break

        created_count = 0
        for topic_name in ALL_TOPICS:
            if topic_name in existing_topics:
                logger.info(f"ℹ️ Тема '{topic_name}' уже существует, пропускаю")
                continue
            
            try:
                random_id = random.randint(0, 2**63 - 1)
                await client(SendMessageRequest(
                    peer=group,
                    message=f"📌 **{topic_name}**\n\n(Тема создана автоматически)",
                    reply_to_msg_id=0,
                    random_id=random_id
                ))
                logger.info(f"✅ Создана тема: {topic_name}")
                created_count += 1
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"❌ Ошибка создания темы '{topic_name}': {e}")

        logger.info(f"🎉 Менеджер тем завершил работу. Создано {created_count} новых тем.")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в менеджере тем: {e}")
    finally:
        await client.disconnect()
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

# ===== ОСНОВНОЙ БОТ (РЕПОСТЫ) =====
async def get_topic_ids(ai_logger):
    if not os.path.exists(SESSION_B64_FILE):
        await ai_logger.log_step("Проверка сессии", "Сессия не найдена!", False)
        return {}

    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        await ai_logger.log_error(e, "Декодирование сессии", "Проверь корректность session.b64")
        return {}

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    ai_logger.client = client
    await ai_logger.log_step("Подключение к аккаунту", "Успешно", True)

    try:
        dialogs = await client.get_dialogs()
        topics = {}
        for dialog in dialogs:
            if dialog.entity.id == TARGET_GROUP_ID and hasattr(dialog, 'forum_topics'):
                if dialog.forum_topics:
                    for topic in dialog.forum_topics:
                        topics[topic.title] = topic.id
                    break
        await ai_logger.log_step("Загрузка тем", f"Найдено {len(topics)} тем", True)
        await client.disconnect()
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return topics
    except Exception as e:
        await ai_logger.log_error(e, "Получение тем", "Проверь права доступа к группе")
        await client.disconnect()
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return {}

async def process_albums(limit=100):
    ai_logger = AILogger(None)
    await ai_logger.log_step("Запуск основного бота", f"Начинаю обработку {limit} сообщений", True)

    if not os.path.exists(SESSION_B64_FILE):
        await ai_logger.log_step("Сессия", "Файл сессии отсутствует", False)
        return False

    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        await ai_logger.log_error(e, "Загрузка сессии", "Проверь права на файлы")
        return False

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    ai_logger.client = client
    await ai_logger.log_step("Подключение к аккаунту", "Успешно", True)

    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
        await ai_logger.log_step("Подключение к каналу", f"Канал {SOURCE_CHANNEL} найден", True)
    except Exception as e:
        await ai_logger.log_error(e, "Получение канала", "Проверь правильность SOURCE_CHANNEL")
        await client.disconnect()
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
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

    await ai_logger.log_step("Получение истории", f"Получено {len(history.messages)} сообщений", True)

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

    await ai_logger.log_step("Обработка альбомов", f"Найдено {len(albums)} альбомов", True)
    await client.disconnect()
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

    if not albums:
        await ai_logger.log_step("Результат", "Альбомы не найдены", False)
        return True

    total_sent = 0
    for idx, album in enumerate(albums):
        text = replace_mentions(album["text"])
        topic = detect_topic(text)
        photos = album["photo_paths"]

        success = False
        for attempt in range(3):
            try:
                client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
                await client.connect()
                ai_logger.client = client
                group = await client.get_entity(TARGET_GROUP_ID)

                topic_ids = await get_topic_ids(ai_logger)
                thread_id = topic_ids.get(topic) if topic_ids else None

                if not thread_id:
                    await ai_logger.send_report(
                        f"⚠️ Новая тема: '{topic}'\nАльбом отправлен в **General**.\nСоздай тему вручную.",
                        "WARNING"
                    )
                    thread_id = None

                caption = f"📌 **{topic}**\n\n{text}" if text else None
                await client.send_file(
                    entity=group,
                    file=photos,
                    caption=caption,
                    parse_mode="markdown",
                    message_thread_id=thread_id
                )

                await ai_logger.log_step(
                    f"Отправка альбома #{idx+1}",
                    f"{len(photos)} фото в '{topic if thread_id else 'General'}'",
                    True
                )
                total_sent += 1
                success = True
                await client.disconnect()
                if os.path.exists(SESSION_FILE):
                    os.remove(SESSION_FILE)
                break

            except Exception as e:
                await ai_logger.log_error(e, f"Попытка #{attempt+1} отправки", f"Ошибка: {e}")
                await client.disconnect()
                if os.path.exists(SESSION_FILE):
                    os.remove(SESSION_FILE)
                await asyncio.sleep(2)

        if not success:
            await ai_logger.send_report(f"🚫 Альбом #{idx+1} не отправлен. Пропускаю.", "WARNING")

    await ai_logger.log_step("Завершение", f"Обработано {total_sent} альбомов", True)
    await ai_logger.send_report(f"🎉 Основной бот завершил работу! Отправлено {total_sent} альбомов.")
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
    asyncio.run(create_all_topics())
    asyncio.run(process_albums(limit=100))
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
