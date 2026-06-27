import asyncio
import time
import re
import logging
import os
import base64
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_FILE = 'session.session'
SESSION_B64_FILE = 'session.b64'
SOURCE_CHANNEL = '@blvckrooom'
TARGET_GROUP = -1003991874844
MENTION_REPLACE = '@esen_baevich'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def copy_posts():
    if not os.path.exists(SESSION_B64_FILE):
        logger.error("❌ Файл сессии не найден!")
        return

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
        logger.info("✅ Сессия загружена")
    except:
        return

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    logger.info("✅ Подключено к аккаунту")

    channel = await client.get_entity(SOURCE_CHANNEL)

    last_id = 0
    while True:
        try:
            history = await client(GetHistoryRequest(
                peer=channel,
                limit=5,
                offset_date=0,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))
            for msg in reversed(history.messages):
                if msg.id > last_id and msg.message:
                    text = re.sub(r'@\w+', MENTION_REPLACE, msg.message)
                    await client.send_message(TARGET_GROUP, text)
                    logger.info(f"📦 Отправлено: {text[:50]}...")
                    last_id = msg.id
                    time.sleep(2)
            logger.info("⏳ Ожидание 10 сек...")
            await asyncio.sleep(10)
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            await asyncio.sleep(10)

async def main():
    logger.info("🚀 Запуск...")
    await copy_posts()

if __name__ == "__main__":
    asyncio.run(main())
