import os
import re
import time
import asyncio
import logging
import base64
import requests
from telethon import TelegramClient, functions
from telethon.tl.functions.messages import GetHistoryRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
TARGET_GROUP_ID = -1003991874844
MENTION_REPLACE = '@esen_baevich'

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_FILE = 'session.session'
SESSION_B64_FILE = 'session.b64'
SOURCE_CHANNEL = '@blvckrooom'

TOPIC_IDS = {
    "Ассортимент": 477,
    "Ralph Lauren": 423,
    "GUCCI": 426,
    "FENDI": 425,
    "ZIMMERMANN": 421,
    "Сумки Hermes": 392,
    "Обувь Hermes": 394,
    "Ремень Hermes": 386,
    "Сумки CHANEL": 396,
    "Chanel": 399,
    "Женская одежда": 397,
    "Сумки THE ROW": 398,
    "Сумки MIU MIU": 400,
    "Одежда для детей": 401,
    "Сумки PRADA": 402,
    "CHROME HEARTS": 403,
    "Женская обувь": 404,
    "Сумки YSL": 405,
    "Женская верхняя одежда (Кожа, кашемир)": 406,
    "Ремни": 407,
    "Шарфы и шапки": 408,
    "Одежда Loro/Brunello/Kiton/Zegna": 409,
    "Очки": 410,
    "Украшения Schiaparelli": 411,
    "Сумки Schiaparelli": 412,
    "Dolce&Gabbana": 413,
    "Мужская верхняя одежда": 414,
    "Купальники и пляжная одежда": 415,
    "Сумки Loewe": 416,
    "Сумки Loro Piana": 417,
    "Сумки BOTTEGA VENETA": 418,
    "Классическая мужская обувь": 419,
    "Сумки Louis Vuitton": 420,
    "EXCLUSIVE": 422,
    "BALENCIAGA": 424,
    "Сумки Jacquemus": 427,
    "Сумки BALENCIAGA": 428,
    "Кроссовки Louis Vuitton": 429,
    "Кроссовки [LUXURY SNEAKERS]": 430,
    "Сумки DIOR": 431,
    "Сумки GOYARD": 432,
    "Мужские сумки": 433,
    "Чемоданы и дорожные сумки": 434,
    "Сумки BVLGARI": 435,
    "Сумки Manolo Blahnik": 436,
    "Обувь Alaïa": 437,
    "BURBERRY": 438,
    "Moncler": 439,
    "Обвесы на сумку": 440,
    "Кроссовки BALENCIAGA": 441,
    "Обувь Chanel": 442,
    "Обувь для пляжа и бассейна": 443,
    "Женские сапоги": 444,
    "Обувь Loro/Brunello/Kiton/Zegna": 445,
    "Acne Studios": 446,
    "CHROME HEARTS Украшения из серебра": 447,
    "Сумки Chrome Hearts": 448,
    "Товары для дома": 449,
    "Сумки CELINE": 450,
    "Лоферы Loro Piana": 451,
    "Сумки Maison Margiela": 452,
    "Сумки Acne Studios": 453,
    "Сумки LEMAIRE": 454,
    "Украшения (бижутерия)": 455,
    "CANADA GOOSE": 456,
    "Yves Saint Laurent": 457,
    "AMI Paris": 458,
    "Кроссовки LOEWE": 459,
    "Кроссовки GUCCI": 460,
    "Arcteryx": 461,
    "GIVENCHY": 462,
    "Классическая мужская одежда": 463,
    "MAISON MARGIELA": 464,
    "WELLDONE": 465,
    "AMIRI": 466,
    "Женская обувь II": 467,
    "Сумки Roger Vivier": 468,
    "Сумки Dolce Gabbana": 469,
    "Сумки Alaïa": 470,
    "Зимние куртки": 471,
    "Обувь для детей": 472,
    "Классическая мужская обувь из экзотической кожи": 473,
    "Сумки Ralph Lauren": 474,
    "Сумки MCM": 475,
    "Max Mara": 476,
    "Пальто": 478,
    "alexander wang": 479,
    "ENFANTS RICHES DEPRIMES": 480,
    "Ювелирные украшения": 481,
    "Обувь Louis Vuitton": 482,
    "Сумки MOYNAT PARIS": 483,
}

def detect_topic(text):
    if not text:
        return "Ассортимент"
    text_lower = text.lower()
    if 'prada' in text_lower: return "Сумки PRADA"
    if 'ralph lauren' in text_lower or 'ralphlauren' in text_lower: return "Ralph Lauren"
    if 'gucci' in text_lower: return "GUCCI"
    if 'fendi' in text_lower: return "FENDI"
    if 'zimmermann' in text_lower: return "ZIMMERMANN"
    if 'hermes' in text_lower: return "Сумки Hermes"
    if 'chanel' in text_lower: return "Chanel"
    if 'dior' in text_lower: return "Сумки DIOR"
    if 'louis vuitton' in text_lower: return "Сумки Louis Vuitton"
    if 'balenciaga' in text_lower: return "BALENCIAGA"
    if 'loewe' in text_lower: return "Сумки Loewe"
    if 'bottega veneta' in text_lower: return "Сумки BOTTEGA VENETA"
    if 'givenchy' in text_lower: return "GIVENCHY"
    if 'yves saint laurent' in text_lower: return "Yves Saint Laurent"
    if 'miu miu' in text_lower: return "Сумки MIU MIU"
    if 'the row' in text_lower: return "Сумки THE ROW"
    if 'zegna' in text_lower: return "Одежда Loro/Brunello/Kiton/Zegna"
    if 'loro piana' in text_lower: return "Сумки Loro Piana"
    if 'brunello cucinelli' in text_lower: return "Одежда Loro/Brunello/Kiton/Zegna"
    if 'acne studios' in text_lower: return "Acne Studios"
    if 'maison margiela' in text_lower: return "Сумки Maison Margiela"
    if 'lemaire' in text_lower: return "Сумки LEMAIRE"
    if 'celine' in text_lower: return "Сумки CELINE"
    if 'chrome hearts' in text_lower: return "CHROME HEARTS"
    if 'moncler' in text_lower: return "Moncler"
    if 'burberry' in text_lower: return "BURBERRY"
    if 'canada goose' in text_lower: return "CANADA GOOSE"
    if 'max mara' in text_lower: return "Max Mara"
    if 'mcm' in text_lower: return "Сумки MCM"
    if 'moynat' in text_lower: return "Сумки MOYNAT PARIS"
    if 'юбка' in text_lower: return "Женская одежда"
    if 'платье' in text_lower: return "Женская одежда"
    if 'брюки' in text_lower: return "Женская одежда"
    if 'шорты' in text_lower: return "Женская одежда"
    if 'футболка' in text_lower: return "Женская одежда"
    if 'рубашка' in text_lower: return "Женская одежда"
    if 'топ' in text_lower: return "Женская одежда"
    if 'куртка' in text_lower: return "Зимние куртки"
    if 'пальто' in text_lower: return "Пальто"
    if 'обувь' in text_lower: return "Женская обувь"
    if 'кроссовки' in text_lower: return "Кроссовки [LUXURY SNEAKERS]"
    if 'часы' in text_lower: return "Часы"
    if 'ремень' in text_lower: return "Ремни"
    if 'сумка' in text_lower: return "Ассортимент"
    if 'очки' in text_lower: return "Очки"
    if 'украшения' in text_lower: return "Ювелирные украшения"
    if 'шапка' in text_lower: return "Шарфы и шапки"
    if 'шарф' in text_lower: return "Шарфы и шапки"
    return "Ассортимент"

def replace_mentions(text):
    return re.sub(r'@\w+', MENTION_REPLACE, text)

async def get_channel_albums():
    if not os.path.exists(SESSION_B64_FILE):
        logger.error(f"❌ Файл {SESSION_B64_FILE} не найден!")
        return []

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
        logger.info("✅ Сессия загружена из .b64")
    except Exception as e:
        logger.error(f"❌ Ошибка декодирования: {e}")
        return []

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    logger.info("✅ Подключение через сессию установлено!")
    
    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
    except Exception as e:
        logger.error(f"❌ Не удалось получить канал: {e}")
        return []

    albums = []
    history = await client(GetHistoryRequest(
        peer=channel,
        limit=50,
        offset_date=0,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))
    
    i = 0
    while i < len(history.messages):
        current = history.messages[i]
        
        if not current.photo:
            i += 1
            continue
        
        album_msgs = [current]
        j = i + 1
        while j < len(history.messages):
            next_msg = history.messages[j]
            time_diff = abs(next_msg.date - current.date)
            if next_msg.photo and time_diff.total_seconds() < 5:
                album_msgs.append(next_msg)
                j += 1
            else:
                break
        
        if len(album_msgs) > 1:
            text = album_msgs[-1].message or ""
            photo_paths = []
            for m in album_msgs:
                try:
                    path = await client.download_media(m, file=f"temp_{m.id}.jpg")
                    photo_paths.append(path)
                except:
                    pass
            
            if photo_paths:
                albums.append({
                    "text": text,
                    "photo_paths": photo_paths
                })
                logger.info(f"📚 Найден альбом с {len(photo_paths)} фото")
        
        i = j
    
    logger.info(f"✅ Загружено {len(albums)} альбомов")
    await client.disconnect()
    return albums

async def ensure_topic_exists(topic_name):
    if topic_name in TOPIC_IDS:
        return TOPIC_IDS[topic_name]
    
    logger.info(f"🆕 Создаю новую тему: {topic_name}")
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    group = await client.get_entity(TARGET_GROUP_ID)
    try:
        result = await client(
            functions.channels.CreateForumTopic(
                channel=group,
                title=topic_name
            )
        )
        new_id = result.id
        TOPIC_IDS[topic_name] = new_id
        logger.info(f"✅ Тема '{topic_name}' создана (ID: {new_id})")
    except Exception as e:
        logger.error(f"❌ Ошибка создания темы {topic_name}: {e}")
    await client.disconnect()
    return TOPIC_IDS.get(topic_name)

async def clear_topic_messages(topic_name):
    thread_id = TOPIC_IDS.get(topic_name)
    if not thread_id:
        logger.warning(f"⚠️ Тема '{topic_name}' не найдена, пропускаю очистку")
        return

    logger.info(f"🧹 Очищаю тему: {topic_name} (ID: {thread_id})")
    url = f"https://api.telegram.org/bot{TOKEN}/getChatHistory"
    params = {
        "chat_id": TARGET_GROUP_ID,
        "limit": 50,
        "message_thread_id": thread_id
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if data.get("ok"):
            messages = data.get("result", {}).get("messages", [])
            for msg in messages:
                if msg.get("from", {}).get("is_bot"):
                    del_url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
                    del_payload = {
                        "chat_id": TARGET_GROUP_ID,
                        "message_id": msg["message_id"]
                    }
                    requests.post(del_url, data=del_payload)
                    logger.info(f"🗑️ Удалено в {topic_name}: ID {msg['message_id']}")
    except Exception as e:
        logger.error(f"❌ Ошибка очистки темы {topic_name}: {e}")

async def send_album_to_topic(topic_name, text, photo_paths):
    await clear_topic_messages(topic_name)
    thread_id = await ensure_topic_exists(topic_name)

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    if photo_paths:
        await client.send_file(
            TARGET_GROUP_ID,
            file=photo_paths,
            caption=f"📌 **{topic_name}**\n\n{text}",
            parse_mode="markdown",
            message_thread_id=thread_id,
            album=True
        )
    await client.disconnect()
    logger.info(f"📚 Альбом ({len(photo_paths)} фото) отправлен в {topic_name} (ID: {thread_id})")

async def main_loop():
    logger.info("🚀 Запуск бесконечного цикла...")
    while True:
        try:
            albums = await get_channel_albums()
            if not albums:
                logger.info("Альбомов не найдено, жду 60 сек...")
                await asyncio.sleep(60)
                continue

            for album in albums:
                text = replace_mentions(album["text"])
                topic = detect_topic(text)
                photo_paths = album["photo_paths"]
                await send_album_to_topic(topic, text, photo_paths)
                await asyncio.sleep(6)
            
            logger.info("✅ Цикл завершён, жду 60 сек до следующей проверки...")
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"❌ Ошибка в цикле: {e}")
            await asyncio.sleep(60)

def main():
    asyncio.run(main_loop())

if __name__ == "__main__":
    main()
