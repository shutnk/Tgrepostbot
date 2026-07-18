import os
import time
import requests
import logging
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
SOURCE_CHANNEL = "@blvckrooom"

def tg_request(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, data=data, timeout=15)
        logger.info(f"📡 Запрос: {method} -> {resp.status_code}")
        return resp.json()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return None

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/health")
def health():
    logger.info("🔍 Запуск диагностики...")
    
    # 1. Проверяем, видит ли бот канал
    chat_info = tg_request("getChat", {"chat_id": SOURCE_CHANNEL})
    if chat_info and chat_info.get("ok"):
        logger.info(f"✅ Бот видит канал: {chat_info['result']['title']} (ID: {chat_info['result']['id']})")
    else:
        logger.error(f"❌ Бот НЕ видит канал. Ответ: {chat_info}")
        return jsonify({"status": "error", "reason": "chat_not_found"})
    
    # 2. Проверяем, есть ли посты (пытаемся получить последние 5)
    updates = tg_request("getUpdates", {"offset": 0, "limit": 5})
    if updates and updates.get("ok"):
        if updates.get("result"):
            logger.info(f"✅ Найдено {len(updates['result'])} обновлений")
            for u in updates["result"]:
                if "channel_post" in u:
                    logger.info(f"📩 Пост: {u['channel_post'].get('text', 'медиа')}")
        else:
            logger.warning("⚠️ Обновлений нет (возможно, нет новых постов)")
    else:
        logger.error(f"❌ Ошибка получения обновлений: {updates}")
    
    return jsonify({"status": "diagnostic_complete"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
