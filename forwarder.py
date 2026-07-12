import asyncio
import time
import re
import logging
from telethon import TelegramClient

# ================== НАСТРОЙКИ ==================
API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
PHONE = '+79030406091'
SESSION_FILE = 'session.session'
SOURCE_CHANNEL = '@blvckrooom'

# ================== ID БОТА (ПРАВИЛЬНЫЙ) ==================
BOT_ID = 8927033296

# ================== ЛОГИРОВАНИЕ ==================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== ГЛАВНЫЙ ЦИКЛ ==================
async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        logger.error("❌ Нет сессии! Сначала выполни вход через QR.")
        return

    logger.info("✅ Зашёл в аккаунт. Начинаю мониторинг...")
    channel = await client.get_entity(SOURCE_CHANNEL)

    last_msg_id = 0
    while True:
        try:
            history = await client.get_messages(channel, limit=5)
            for msg in reversed(history):
                if msg.id > last_msg_id and msg.text:
                    text = msg.text
                    if msg.photo:
                        await client.send_file(BOT_ID, msg.media, caption=text)
                        logger.info(f"📸 Фото отправлено боту (ID: {msg.id})")
                    else:
                        await client.send_message(BOT_ID, text)
                        logger.info(f"📝 Текст отправлен боту (ID: {msg.id})")
                    
                    last_msg_id = msg.id
                    time.sleep(3)
            
            logger.info("⏳ Ожидание 10 сек...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            time.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
