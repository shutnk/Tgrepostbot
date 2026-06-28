import time
import re
import logging
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
TARGET_GROUP = -1003991874844
MENTION_REPLACE = '@esen_baevich'
RENDER_EXTERNAL_URL = "https://tgrepostbot.onrender.com"

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

album_buffer = {}

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def do_POST(self):
        if self.path != "/webhook":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            update = json.loads(post_data)
        except:
            self.send_response(200)
            self.end_headers()
            return

        msg = update.get("message")
        if not msg:
            self.send_response(200)
            self.end_headers()
            return

        group_id = msg.get("media_group_id")
        
        if group_id:
            if group_id not in album_buffer:
                album_buffer[group_id] = {"photos": [], "caption": "", "timestamp": time.time()}
            
            if "photo" in msg:
                album_buffer[group_id]["photos"].append(msg["photo"][-1]["file_id"])
            
            if "caption" in msg:
                album_buffer[group_id]["caption"] = msg["caption"]
            
            if time.time() - album_buffer[group_id]["timestamp"] > 2:
                caption = album_buffer[group_id]["caption"]
                new_text = replace_mentions(caption)
                topic = detect_topic(new_text)
                photos = album_buffer[group_id]["photos"]
                del album_buffer[group_id]
                
                url = f"https://api.telegram.org/bot{TOKEN}/sendMediaGroup"
                media = [{"type": "photo", "media": p} for p in photos]
                if caption:
                    media[0]["caption"] = f"📌 **{topic}**\n\n{new_text}"
                    media[0]["parse_mode"] = "Markdown"
                requests.post(url, json={"chat_id": TARGET_GROUP, "media": media})
                logger.info(f"📚 Альбом ({len(photos)} фото) отправлен в {topic}")
                self.send_response(200)
                self.end_headers()
                return
            
            self.send_response(200)
            self.end_headers()
            return

        text = ""
        photo_url = None

        if "photo" in msg:
            photo_list = msg["photo"]
            if photo_list:
                photo_url = photo_list[-1]["file_id"]
            if "caption" in msg:
                text = msg["caption"]
        elif "text" in msg:
            text = msg["text"]
        elif "caption" in msg:
            text = msg["caption"]

        if not text and not photo_url:
            self.send_response(200)
            self.end_headers()
            return

        new_text = replace_mentions(text)
        topic = detect_topic(new_text)

        if photo_url:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            payload = {
                "chat_id": TARGET_GROUP,
                "photo": photo_url,
                "caption": f"📌 **{topic}**\n\n{new_text}",
                "parse_mode": "Markdown"
            }
            requests.post(url, data=payload)
            logger.info(f"📸 Одиночное фото отправлено в {topic}")
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {
                "chat_id": TARGET_GROUP,
                "text": f"📌 **{topic}**\n\n{new_text}",
                "parse_mode": "Markdown"
            }
            requests.post(url, data=payload)
            logger.info(f"📝 Текст отправлен в {topic}")

        self.send_response(200)
        self.end_headers()

def setup_webhook():
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.json().get("ok"):
            logger.info(f"✅ Webhook установлен на: {webhook_url}")
        else:
            logger.error(f"❌ Ошибка установки Webhook: {resp.text}")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Telegram: {e}")

if __name__ == "__main__":
    setup_webhook()
    server = HTTPServer(("0.0.0.0", 10000), WebhookHandler)
    logger.info("🚀 Сервер запущен на порту 10000")
    server.serve_forever()
