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

# ==============================================
#  «ИНТЕЛЛЕКТУАЛЬНОЕ ЯДРО» БОТА (Planner)
# ==============================================
class BotPlanner:
    def __init__(self):
        self.topic_ids = {}
        self.albums = []
        self.sent_ids = set()
        self.last_check = 0

    def analyze_albums(self, new_albums):
        """Анализирует, какие альбомы нужно отправить"""
        if not new_albums:
            return {"action": "wait", "reason": "Нет новых альбомов"}
        
        # Проверяем, не отправляли ли мы их уже
        unsent = []
        for album in new_albums:
            # Простой интеллект: если текст похож на уже отправленный — пропускаем
            if album["text"][:50] not in [s[:50] for s in self.sent_ids]:
                unsent.append(album)
        
        if not unsent:
            return {"action": "wait", "reason": "Все альбомы уже отправлены"}
        
        return {"action": "process", "albums": unsent, "reason": f"Найдено {len(unsent)} новых альбомов"}

    def decide_topic(self, text):
        """Сам решает, в какую тему отправить пост"""
        if not text: return "Ассортимент"
        text_lower = text.lower()
        
        # ЕГО СОБСТВЕННАЯ ЛОГИКА:
        if 'кроссовки' in text_lower: return "Кроссовки [LUXURY SNEAKERS]"
        if 'обувь' in text_lower: return "Обувь Hermes"
        if 'сумка' in text_lower: return "Сумки Hermes"
        
        # Анализ по словарю
        brands = {
            "prada": "Сумки PRADA", "ralph lauren": "Ralph Lauren",
            "gucci": "GUCCI", "fendi": "FENDI", "zimmermann": "ZIMMERMANN",
            "hermes": "Сумки Hermes", "chanel": "Chanel", "dior": "Сумки DIOR",
            "louis vuitton": "Сумки Louis Vuitton", "balenciaga": "BALENCIAGA",
            "loewe": "Сумки Loewe", "bottega veneta": "Сумки BOTTEGA VENETA",
            "givenchy": "GIVENCHY", "yves saint laurent": "Yves Saint Laurent",
            "miu miu": "Сумки MIU MIU", "the row": "Сумки THE ROW",
            "zegna": "Одежда Loro/Brunello/Kiton/Zegna", "loro piana": "Сумки Loro Piana",
            "brunello cucinelli": "Одежда Loro/Brunello/Kiton/Zegna",
            "acne studios": "Acne Studios", "maison margiela": "Сумки Maison Margiela",
            "lemaire": "Сумки LEMAIRE", "celine": "Сумки CELINE",
            "chrome hearts": "CHROME HEARTS", "moncler": "Moncler",
            "burberry": "BURBERRY", "canada goose": "CANADA GOOSE",
            "max mara": "Max Mara", "mcm": "Сумки MCM", "moynat": "Сумки MOYNAT PARIS",
        }
        for key, topic in brands.items():
            if key in text_lower:
                return topic
        
        return "Ассортимент"

# ==============================================
#  ЗАПУСК
# ==============================================
planner = BotPlanner()

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
        result = await client(
            functions.channels.GetForumTopics(
                channel=group,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100
            )
        )
        topic_ids = {t.title: t.id for t in result.topics}
        logger.info(f"🧠 Загружено {len(topic_ids)} тем")
        await client.disconnect()
        return topic_ids
    except Exception as e:
        logger.error(f"❌ Ошибка получения тем: {e}")
        await client.disconnect()
        return {}

async def get_channel_albums(limit=100):
    if not os.path.exists(SESSION_B64_FILE):
        logger.error("❌ Нет сессии!")
        return []

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки сессии: {e}")
        return []

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
    except Exception as e:
        logger.error(f"❌ Не удалось получить канал: {e}")
        await client.disconnect()
        return []

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
    return albums

async def send_album(topic, text, photos):
    thread_id = planner.topic_ids.get(topic)
    if not thread_id:
        logger.warning(f"⚠️ Тема '{topic}' не найдена, пытаюсь создать...")
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.connect()
        group = await client.get_entity(TARGET_GROUP_ID)
        try:
            result = await client(
                functions.channels.CreateForumTopic(
                    channel=group,
                    title=topic
                )
            )
            thread_id = result.id
            planner.topic_ids[topic] = thread_id
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
        planner.sent_ids.add(text[:50])
        logger.info(f"📚 Альбом ({len(photos)} фото) в {topic} (ID: {thread_id})")
        return True
    return False

async def main_loop():
    logger.info("🧠 Запуск интеллектуального бота...")
    planner.topic_ids = await get_topic_ids()

    while True:
        try:
            # 1. Бот получает данные
            albums = await get_channel_albums(limit=50)
            
            # 2. Бот анализирует
            decision = planner.analyze_albums(albums)
            logger.info(f"🧠 Решение: {decision['action']} — {decision.get('reason', '')}")
            
            if decision["action"] == "process":
                for album in decision["albums"]:
                    # 3. Бот принимает решение о теме
                    topic = planner.decide_topic(album["text"])
                    text = re.sub(r'@\w+', MENTION_REPLACE, album["text"])
                    photos = album["photo_paths"]
                    
                    # 4. Бот выполняет
                    await send_album(topic, text, photos)
                    await asyncio.sleep(3)
            
            # 5. Бот решает, сколько ждать
            wait_time = 10 if decision["action"] == "process" else 30
            logger.info(f"🧠 Ожидание {wait_time} секунд...")
            await asyncio.sleep(wait_time)
        
        except Exception as e:
            logger.error(f"❌ Ошибка цикла: {e}")
            await asyncio.sleep(30)

# ==============================================
#  FLASK ДЛЯ ОЖИВЛЕНИЯ
# ==============================================
@app.route("/")
def index():
    return "Bot is running!"

@app.route("/health")
def health():
    return jsonify({"status": "ok", "intelligence": "active"})

if __name__ == "__main__":
    asyncio.run(main_loop())
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
