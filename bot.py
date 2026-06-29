import os
import re
import time
import asyncio
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

# === ID ТЕМ ===
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
    "FENDI": 425,
    "GUCCI": 426,
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

# === БОЛЕЕ ТОЧНОЕ ОПРЕДЕЛЕНИЕ ТЕМ (включая хэштеги) ===
TOPIC_MAP = {
    "hermes": "Сумки Hermes",
    "ralph lauren": "Ralph Lauren",
    "fendi": "FENDI",
    "gucci": "GUCCI",
    "zimmermann": "ZIMMERMANN",
    "prada": "Сумки PRADA",
    "chanel": "Chanel",
    "dior": "Сумки DIOR",
    "louis vuitton": "Сумки Louis Vuitton",
    "balenciaga": "BALENCIAGA",
    "loewe": "Сумки Loewe",
    "bottega veneta": "Сумки BOTTEGA VENETA",
    "givenchy": "GIVENCHY",
    "yves saint laurent": "Yves Saint Laurent",
    "miu miu": "Сумки MIU MIU",
    "prada": "Сумки PRADA",
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
    # Категории
    "юбка": "Женская одежда",
    "платье": "Женская одежда",
    "брюки": "Женская одежда",
    "шорты": "Женская одежда",
    "футболка": "Женская одежда",
    "рубашка": "Женская одежда",
    "топ": "Женская одежда",
    "куртка": "Зимние куртки",
    "пальто": "Пальто",
    "обувь": "Женская обувь",
    "кроссовки": "Кроссовки [LUXURY SNEAKERS]",
    "часы": "Часы",
    "ремень": "Ремни",
    "сумка": "Ассортимент",
    "очки": "Очки",
    "украшения": "Ювелирные украшения",
    "шапка": "Шарфы и шапки",
    "шарф": "Шарфы и шапки",
    "ремень": "Ремни",
    "аксессуары": "Ассортимент",
    "одежда": "Ассортимент",
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
        msg = history.messages[i]
        if not msg.grouped_id:
            i += 1
            continue
        
        album_msgs = [msg]
        j = i + 1
        while j < len(history.messages):
            next_msg = history.messages[j]
            if next_msg.grouped_id == msg.grouped_id:
                album_msgs.append(next_msg)
                j += 1
            else:
                break
        
        if len(album_msgs) > 1:
            text = album_msgs[-1].message or ""
            unique_photo_paths = set()  # <-- УБИРАЕМ ДУБЛИКАТЫ
            for m in album_msgs:
                try:
                    path = await client.download_media(m, file=f"temp_{m.id}.jpg")
                    if path:
                        unique_photo_paths.add(path)
                except:
                    pass
            
            if unique_photo_paths:
                albums.append({
                    "text": text,
                    "photo_paths": list(unique_photo_paths)
                })
                logger.info(f"📚 Найден альбом с {len(unique_photo_paths)} уникальными фото")
        
        i = j
    
    logger.info(f"✅ Загружено {len(albums)} альбомов с уникальными фото")
    await client.disconnect()
    return albums

def send_album_to_topic(topic_name, text, photo_paths):
    thread_id = TOPIC_IDS.get(topic_name)
    if not thread_id:
        logger.warning(f"⚠️ Тема '{topic_name}' не найдена, отправляю в общий чат")
        thread_id = 1

    async def send_telethon():
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.connect()
        if photo_paths:
            await client.send_file(
                TARGET_GROUP_ID,
                file=photo_paths,
                caption=f"📌 **{topic_name}**\n\n{text}",
                parse_mode="markdown",
                message_thread_id=thread_id,
                force_document=False,
                album=True
            )
        await client.disconnect()
    
    try:
        asyncio.run(send_telethon())
        logger.info(f"📚 Альбом ({len(photo_paths)} фото) отправлен в {topic_name} (ID: {thread_id})")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки альбома: {e}")

def main():
    logger.info("🚀 Запуск финального копирования...")
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
