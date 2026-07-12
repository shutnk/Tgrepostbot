import os
import asyncio
import logging
import base64
from telethon import TelegramClient
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.channels import GetForumTopicsRequest
import random

# ===== НАСТРОЙКИ =====
API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_FILE = 'session.session'
SESSION_B64_FILE = 'session.b64'
TARGET_GROUP_ID = -1003991874844

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_topic(topic_name):
    """
    Создаёт тему через твою сессию (от имени @nurikadambol).
    Возвращает ID темы или None.
    """
    if not os.path.exists(SESSION_B64_FILE):
        logger.error("❌ Нет сессии!")
        return None

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки сессии: {e}")
        return None

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    
    try:
        group = await client.get_entity(TARGET_GROUP_ID)
        
        # Проверяем, есть ли уже такая тема
        try:
            result = await client(GetForumTopicsRequest(
                channel=group,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100
            ))
            for topic in result.topics:
                if topic.title == topic_name:
                    logger.info(f"✅ Тема '{topic_name}' уже существует (ID: {topic.id})")
                    await client.disconnect()
                    return topic.id
        except:
            pass
        
        # Если темы нет — создаём через SendMessageRequest с reply_to_msg_id=0
        random_id = random.randint(0, 2**63 - 1)
        await client(SendMessageRequest(
            peer=group,
            message=f"📌 **{topic_name}**\n\n(Тема создана ботом @trifferitopicbot)",
            reply_to_msg_id=0,
            random_id=random_id
        ))
        
        logger.info(f"✅ Команда на создание темы '{topic_name}' отправлена")
        
        # Даём Telegram время на создание темы
        await asyncio.sleep(3)
        
        # Пытаемся получить ID новой темы
        try:
            result = await client(GetForumTopicsRequest(
                channel=group,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100
            ))
            for topic in result.topics:
                if topic.title == topic_name:
                    logger.info(f"✅ Тема '{topic_name}' успешно создана (ID: {topic.id})")
                    await client.disconnect()
                    return topic.id
        except:
            pass
        
        logger.warning(f"⚠️ Тема '{topic_name}' создана, но ID не найден")
        await client.disconnect()
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания темы '{topic_name}': {e}")
        await client.disconnect()
        return None

async def main():
    # Для теста: создаём тему "Сумки Hermes"
    topic_id = await create_topic("Сумки Hermes")
    if topic_id:
        print(f"✅ Тема создана с ID: {topic_id}")
    else:
        print("❌ Не удалось создать тему")

if __name__ == "__main__":
    asyncio.run(main())
