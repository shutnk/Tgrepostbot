import time
import requests
import re
import logging
from bs4 import BeautifulSoup

BOT_TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
SOURCE_CHANNEL = "blvckrooom"
BOT_USERNAME = "YOUR_BOT_USERNAME"  # ВСТАВЬ ИМЯ БЕЗ @ (например, trifferi_catalog_bot)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_latest_posts():
    url = f"https://t.me/s/{SOURCE_CHANNEL}"
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        posts = []
        for div in soup.find_all('div', class_='tgme_widget_message'):
            text_div = div.find('div', class_='tgme_widget_message_text')
            text = text_div.get_text() if text_div else ""
            if text:
                posts.append(text)
        return posts
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return []

def send_to_bot(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": BOT_USERNAME,
        "text": text
    }
    try:
        requests.post(url, data=payload, timeout=10)
        logger.info("✅ Отправлено боту в ЛС")
    except:
        pass

def main():
    last_text = ""
    logger.info("🚀 Авто-форвардер запущен...")
    while True:
        posts = get_latest_posts()
        if posts:
            for text in reversed(posts):
                if text != last_text:
                    send_to_bot(text)
                    last_text = text
                    time.sleep(3)
        time.sleep(10)

if __name__ == "__main__":
    main()
