import os
import time
import requests
import re
import logging
import xml.etree.ElementTree as ET

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
TARGET_GROUP_ID = -1003991874844
SOURCE_CHANNEL = "blvckrooom"
RSS_URL = f"https://t.me/s/{SOURCE_CHANNEL}.rss"

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
    "сумки moynat paris": "Сумки MOYNAT PARIS"
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
    return re.sub(r'@\w+', '@esen_baevich', text)

def get_channel_posts_rss():
    try:
        response = requests.get(RSS_URL, timeout=20)
        if response.status_code != 200:
            logger.error(f"RSS ошибка: код {response.status_code}")
            return []
        
        root = ET.fromstring(response.text)
        posts = []
        
        # В RSS посты находятся в <item>
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            desc_elem = item.find('description')
            
            title = title_elem.text if title_elem is not None else ""
            desc = desc_elem.text if desc_elem is not None else ""
            
            # Объединяем заголовок и описание
            full_text = f"{title}\n\n{desc}"
            
            # Ищем картинку в описании (часто бывает в HTML)
            image_url = ""
            if desc:
                img_match = re.search(r'<img[^>]+src="([^"]+)"', desc)
                if img_match:
                    image_url = img_match.group(1)
            
            if full_text.strip():
                posts.append({
                    "text": full_text,
                    "image": image_url
                })
        
        logger.info(f"✅ RSS: Найдено {len(posts)} постов.")
        return posts
    except Exception as e:
        logger.error(f"Ошибка RSS: {e}")
        return []

def send_to_topic(topic_name, text, image_url=None):
    if image_url and image_url.startswith("http"):
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": TARGET_GROUP_ID,
            "photo": image_url,
            "caption": f"📌 **{topic_name}**\n\n{text}",
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, data=payload, timeout=15)
            return
        except:
            pass
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": TARGET_GROUP_ID,
        "text": f"📌 **{topic_name}**\n\n{text}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload, timeout=15)
    except:
        pass

def main():
    logger.info("🚀 Запуск парсинга через RSS...")
    posts = get_channel_posts_rss()
    
    if not posts:
        logger.info("Постов не найдено в RSS.")
        return
    
    for post in posts:
        text = post.get("text", "")
        image = post.get("image", "")
        if text:
            topic = detect_topic(text)
            new_text = replace_mentions(text)
            send_to_topic(topic, new_text, image)
            logger.info(f"📦 Отправлено в {topic}: {new_text[:50]}...")
            time.sleep(3)

if __name__ == "__main__":
    main()
