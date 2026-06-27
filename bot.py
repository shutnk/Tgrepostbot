import os
import base64
import asyncio
import time
import re
import logging
import io
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_FILE = 'session.session'
SOURCE_CHANNEL = '@blvckrooom'
TARGET_GROUP = -1003991874844
MENTION_REPLACE = '@esen_baevich'

# === СЛОВАРЬ ТЕМ ===
TOPIC_MAP = {
    "сумки hermes": "Сумки Hermes",
    "обувь hermes": "Обувь Hermes",
    "ремень hermes": "Ремень Hermes",
    "сумки chanel": "Сумки CHANEL",
    "chanel": "Chanel",
    "женская одежда": "Женская одежда",
    "сумки the row": "Сумки THE ROW",
    "сумки miu miu": "Сумки MIU MIU",
    "одежда для детей": "Одежда для детей",
    "сумки prada": "Сумки PRADA",
    "chrome hearts": "CHROME HEARTS",
    "женская обувь": "Женская обувь",
    "сумки ysl": "Сумки YSL",
    "женская верхняя одежда": "Женская верхняя одежда (Кожа, кашемир)",
    "ремни": "Ремни",
    "шарфы и шапки": "Шарфы и шапки",
    "очки": "Очки",
    "украшения schiaparelli": "Украшения Schiaparelli",
    "сумки schiaparelli": "Сумки Schiaparelli",
    "dolce&gabbana": "Dolce&Gabbana",
    "мужская верхняя одежда": "Мужская верхняя одежда",
    "купальники": "Купальники и пляжная одежда",
    "сумки loewe": "Сумки Loewe",
    "сумки loro piana": "Сумки Loro Piana",
    "сумки bottega veneta": "Сумки BOTTEGA VENETA",
    "классическая мужская обувь": "Классическая мужская обувь",
    "сумки louis vuitton": "Сумки Louis Vuitton",
    "zimmermann": "ZIMMERMANN",
    "exclusive": "EXCLUSIVE",
    "ralph lauren": "Ralph Lauren",
    "balenciaga": "BALENCIAGA",
    "fendi": "FENDI",
    "gucci": "GUCCI",
    "сумки jacquemus": "Сумки Jacquemus",
    "кроссовки louis vuitton": "Кроссовки Louis Vuitton",
    "кроссовки luxury": "Кроссовки [LUXURY SNEAKERS]",
    "сумки dior": "Сумки DIOR",
    "сумки goyard": "Сумки GOYARD",
    "мужские сумки": "Мужские сумки",
    "чемоданы": "Чемоданы и дорожные сумки",
    "сумки bvlgari": "Сумки BVLGARI",
    "сумки manolo blahnik": "Сумки Manolo Blahnik",
    "обувь alaïa": "Обувь Alaïa",
    "burberry": "BURBERRY",
    "moncler": "Moncler",
    "обвесы на сумку": "Обвесы на сумку",
    "обувь chanel": "Обувь Chanel",
    "обувь для пляжа": "Обувь для пляжа и бассейна",
    "женские сапоги": "Женские сапоги",
    "acne studios": "Acne Studios",
    "сумки chrome hearts": "Сумки Chrome Hearts",
    "товары для дома": "Товары для дома",
    "сумки celine": "Сумки CELINE",
    "лоферы loro piana": "Лоферы Loro Piana",
    "сумки maison margiela": "Сумки Maison Margiela",
    "сумки acne studios": "Сумки Acne Studios",
    "сумки lemaire": "Сумки LEMAIRE",
    "бижутерия": "Украшения (бижутерия)",
    "canada goose": "CANADA GOOSE",
    "yves saint laurent": "Yves Saint Laurent",
    "ami paris": "AMI Paris",
    "кроссовки loewe": "Кроссовки LOEWE",
    "кроссовки gucci": "Кроссовки GUCCI",
    "arcteryx": "Arcteryx",
    "givenchy": "GIVENCHY",
    "классическая мужская одежда": "Классическая мужская одежда",
    "maison margiela": "MAISON MARGIELA",
    "welldone": "WELLDONE",
    "amiri": "AMIRI",
    "женская обувь ii": "Женская обувь II",
    "сумки roger vivier": "Сумки Roger Vivier",
    "сумки dolce gabbana": "Сумки Dolce Gabbana",
    "сумки alaïa": "Сумки Alaïa",
    "зимние куртки": "Зимние куртки",
    "обувь для детей": "Обувь для детей",
    "экзотическая кожа": "Классическая мужская обувь из экзотической кожи",
    "сумки ralph lauren": "Сумки Ralph Lauren",
    "сумки mcm": "Сумки MCM",
    "max mara": "Max Mara",
    "ассортимент": "Ассортимент",
    "пальто": "Пальто",
    "alexander wang": "alexander wang",
    "enfants riches deprimes": "ENFANTS RICHES DEPRIMES",
    "ювелирные украшения": "Ювелирные украшения",
    "сумки moynat paris": "Сумки MOYNAT PARIS",
    
    "браслет": "Ювелирные украшения",
    "серьги": "Ювелирные украшения",
    "колье": "Ювелирные украшения",
    "подвеска": "Ювелирные украшения",
    "vivienne westwood": "Ювелирные украшения",
    "кольцо": "Ювелирные украшения",
    "цепи": "Ювелирные украшения",
    "украшения": "Ювелирные украшения",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

topic_ids = {}

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

async def load_topic_ids(client):
    global topic_ids
    try:
        group = await client.get_entity(TARGET_GROUP)
        # Прямой вызов API вместо импорта
        result = await client(
            client._get_api().channels.GetForumTopics(
                channel=group,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100
            )
        )
        for topic in result.topics:
            topic_ids[topic.title] = topic.id
        logger.info(f"✅ Загружено ID тем: {list(topic_ids.keys())}")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки ID: {e}")

async def copy_posts():
    global topic_ids
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    logger.info("✅ Подключение через сессию установлено!")
    
    await load_topic_ids(client)
    
    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
    except Exception as e:
        logger.error(f"❌ Не удалось получить канал: {e}")
        return

    last_msg_id = 0
    while True:
        try:
            history = await client(GetHistoryRequest(
                peer=channel,
                limit=10,
                offset_date=0,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))
            
            for msg in reversed(history.messages):
                if msg.id > last_msg_id and msg.message:
                    text = msg.message
                    topic = detect_topic(text)
                    new_text = replace_mentions(text)
                    
                    thread_id = topic_ids.get(topic)
                    if not thread_id:
                        thread_id = topic_ids.get("Ассортимент")
                    
                    if thread_id:
                        # Скачиваем медиа, если есть
                        media_file = None
                        if msg.media:
                            try:
                                media_file = await client.download_media(msg, file=io.BytesIO())
                            except:
                                pass
                        
                        if media_file:
                            # Отправляем с фото/видео
                            await client.send_file(
                                TARGET_GROUP,
                                file=media_file,
                                caption=f"📌 **{topic}**\n\n{new_text}",
                                message_thread_id=thread_id,
                                parse_mode="markdown"
                            )
                        else:
                            # Отправляем только текст
                            await client.send_message(
                                TARGET_GROUP,
                                f"📌 **{topic}**\n\n{new_text}",
                                message_thread_id=thread_id
                            )
                        logger.info(f"📦 Отправлено в {topic} (ID: {thread_id}): {new_text[:50]}...")
                    else:
                        logger.error(f"❌ Нет ID для темы: {topic}")
                    
                    last_msg_id = msg.id
                    time.sleep(2)
            
            logger.info("⏳ Ожидание 10 сек...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"❌ Ошибка цикла: {e}")
            time.sleep(10)

async def main():
    logger.info("🚀 Запуск с медиа и темами...")
    await copy_posts()

if __name__ == "__main__":
    asyncio.run(main())
