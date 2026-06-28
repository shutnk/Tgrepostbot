import time
import re
import logging
import requests

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
TARGET_GROUP = -1003991874844
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

def main():
    offset = 0
    logger.info("🚀 Запуск бота-приёмника (с поддержкой фото)...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            resp = requests.get(url, timeout=35)
            data = resp.json()
            if not data.get("ok"):
                continue
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message")
                if not msg:
                    continue
                
                # ===== ПОДДЕРЖКА МЕДИА И ТЕКСТА =====
                text = ""
                if "caption" in msg:
                    text = msg["caption"]
                elif "text" in msg:
                    text = msg["text"]
                
                if not text:
                    continue
                
                topic = detect_topic(text)
                new_text = replace_mentions(text)
                
                send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                payload = {
                    "chat_id": TARGET_GROUP,
                    "text": f"📌 **{topic}**\n\n{new_text}",
                    "parse_mode": "Markdown"
                }
                requests.post(send_url, data=payload)
                logger.info(f"📦 Принят в ЛС и отправлен в {topic}")
                time.sleep(1)
        except Exception as e:
            logger.error(f"❌ Ошибка цикла: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
