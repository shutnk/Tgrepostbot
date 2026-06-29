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
TARGET_GROUP_USERNAME = "trifferi_katalog"

MENTION_REPLACE = '@esen_baevich'

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_FILE = 'session.session'
SESSION_B64_FILE = 'session.b64'
SOURCE_CHANNEL = '@blvckrooom'

# === РУЧНОЕ СООТВЕТСТВИЕ ТЕМ ===
TOPIC_IDS = {
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
    "ZIMMERMANN": 421,
    "EXCLUSIVE": 422,
    "Ralph Lauren": 423,
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
    "Ассортимент": 477,
    "Пальто": 478,
    "alexander wang": 479,
    "ENFANTS RICHES DEPRIMES": 480,
    "Ювелирные украшения": 481,
    "Обувь Louis Vuitton": 482,
    "Сумки MOYNAT PARIS": 483,
}

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
        if msg.message:
            text = msg.message
            photo_url = None
            if msg.media:
                try:
                    photo_path = await client.download_media(msg, file="temp_photo.jpg")
                    photo_url = photo_path
                except:
                    photo_url = None
            posts.append({"text": text, "photo_url": photo_url})
    logger.info(f"✅ Загружено {len(posts)} постов из канала")
    await client.disconnect()
    return posts

def send_to_topic(topic_name, text, photo_url=None):
    thread_id = TOPIC_IDS.get(topic_name)
    
    if not thread_id:
        logger.warning(f"⚠️ Тема '{topic_name}' не найдена в словаре, отправляю в общий чат")
        thread_id = 1

    if photo_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': open(photo_url, 'rb')}
        payload = {
            "chat_id": TARGET_GROUP_ID,
            "caption": f"📌 **{topic_name}**\n\n{text}",  # <-- ТЕПЕРЬ ТЕКСТ ДОБАВЛЕН
            "parse_mode": "Markdown",
            "message_thread_id": thread_id
        }
        requests.post(url, files=files, data=payload)
        logger.info(f"📸 Фото + текст отправлено в {topic_name} (ID: {thread_id})")
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": TARGET_GROUP_ID,
            "text": f"📌 **{topic_name}**\n\n{text}",
            "parse_mode": "Markdown",
            "message_thread_id": thread_id
        }
        requests.post(url, data=payload)
        logger.info(f"📝 Текст отправлен в {topic_name} (ID: {thread_id})")

def main():
    logger.info("🚀 Запуск финального копирования...")
    posts = asyncio.run(get_channel_posts())
    if not posts:
        logger.info("Постов не найдено.")
        return

    for post in posts:
        text = replace_mentions(post["text"])
        topic = detect_topic(text)
        photo = post.get("photo_url")
        send_to_topic(topic, text, photo)
        time.sleep(3)

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_fake_server, daemon=True)
    http_thread.start()
    main()
