import requests
import time
import logging

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = "@trifferi_katalog"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_topics():
    """Получает список всех тем в группе"""
    url = f"https://api.telegram.org/bot{TOKEN}/getForumTopics"
    payload = {"chat_id": CHAT_ID}
    try:
        resp = requests.post(url, data=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            return data["result"].get("topics", [])
        else:
            logger.error(f"Ошибка получения тем: {data.get('description')}")
            return []
    except Exception as e:
        logger.error(f"Ошибка запроса: {e}")
        return []

def delete_topic(topic_id, topic_name):
    """Удаляет конкретную тему по ID"""
    url = f"https://api.telegram.org/bot{TOKEN}/deleteForumTopic"
    payload = {"chat_id": CHAT_ID, "message_thread_id": topic_id}
    try:
        resp = requests.post(url, data=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            logger.info(f"✅ Удалена тема: {topic_name} (ID: {topic_id})")
            return True
        else:
            logger.error(f"❌ Ошибка удаления {topic_name}: {data.get('description')}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка запроса при удалении {topic_name}: {e}")
        return False

def main():
    logger.info("🚀 Начинаю получение списка тем...")
    topics = get_all_topics()
    
    if not topics:
        logger.info("Тем не найдено или произошла ошибка.")
        return

    logger.info(f"Найдено тем для удаления: {len(topics)}")
    
    deleted = 0
    errors = 0

    for topic in topics:
        topic_id = topic.get("message_thread_id")
        topic_name = topic.get("name", "Без названия")
        
        # Пропускаем общую тему (General), она не удаляется
        if topic_id == 1:
            logger.info("➖ Пропущена общая тема (General)")
            continue

        if delete_topic(topic_id, topic_name):
            deleted += 1
        else:
            errors += 1
        
        # Небольшая пауза, чтобы не перегружать API
        time.sleep(1)

    logger.info(f"🏁 ЗАВЕРШЕНО. Удалено: {deleted}, Ошибок: {errors}")

if __name__ == "__main__":
    main()
