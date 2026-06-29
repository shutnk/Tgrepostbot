import os
import re
import time
import requests
import logging
import base64
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
TARGET_GROUP_ID = -1003991874844
TARGET_GROUP_USERNAME = "trifferi_katalog"

MENTION_REPLACE = '@esen_baevich'

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

# === ПАРСИМ ТЕМЫ ПРЯМО ИЗ ССЫЛОК ГРУППЫ ===
def get_topic_ids_from_html():
    url = f"https://t.me/s/{TARGET_GROUP_USERNAME}"
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            logger.error(f"❌ Не удалось загрузить страницу: {resp.status_code}")
            return {}
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        topic_ids = {}
        
        links = soup.find_all('a', href=re.compile(rf'/{TARGET_GROUP_USERNAME}/\d+'))
        for link in links:
            href = link.get('href')
            match = re.search(rf'/{TARGET_GROUP_USERNAME}/(\d+)', href)
            if match:
                topic_id = int(match.group(1))
                parent = link.find_parent('div', class_='tgme_widget_message')
                if parent:
                    text_div = parent.find('div', class_='tgme_widget_message_text')
                    if text_div:
                        topic_name = text_div.get_text().strip()
                        if topic_name:
                            topic_ids[topic_name] = topic_id
        
        logger.info(f"✅ Загружено ID тем из HTML: {list(topic_ids.keys())}")
        return topic_ids
    except Exception as e:
        logger.error(f"❌ Ошибка парсинга тем: {e}")
        return {}

def send_to_topic(topic_name, text, photo_url=None):
    topic_ids = get_topic_ids_from_html()
    thread_id = topic_ids.get(topic_name)
    
    if not thread_id:
        logger.warning(f"⚠️ Тема '{topic_name}' не найдена, отправляю в общий чат")
        thread_id = 1

    if photo_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": TARGET_GROUP_ID,
            "photo": photo_url,
            "caption": f"📌 **{topic_name}**\n\n{text}",
            "parse_mode": "Markdown",
            "message_thread_id": thread_id
        }
        requests.post(url, data=payload)
        logger.info(f"📸 Фото отправлено в {topic_name} (ID: {thread_id})")
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
    logger.info("🚀 Запуск финального копирования через HTML-парсинг...")
    
    # ВСТАВЬ СЮДА КОД ПОЛУЧЕНИЯ ПОСТОВ ИЗ КАНАЛА
    # Например, через Telethon или Requests
    logger.info("Здесь должен быть код получения постов из @blvckrooom")
    # Пример:
    # posts = get_posts_from_channel()
    # for post in posts:
    #     topic = detect_topic(post["text"])
    #     send_to_topic(topic, post["text"], post.get("photo_url"))

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_fake_server, daemon=True)
    http_thread.start()
    main()
