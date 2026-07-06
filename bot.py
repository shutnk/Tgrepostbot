import os
import re
import asyncio
import logging
import base64
import json
import traceback
import sys
from flask import Flask, jsonify
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

# ===== НАСТРОЙКИ =====
API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_FILE = 'session.session'
SESSION_B64_FILE = 'session.b64'
SOURCE_CHANNEL = '@blvckrooom'
TARGET_GROUP_ID = -1003991874844
MENTION_REPLACE = '@esen_baevich'

ADMIN_ID = 5468112563

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# ===== ЛОГГЕР =====
class AILogger:
    def __init__(self, client=None):
        self.client = client
        self.error_count = 0
        self.max_errors = 3

    async def send_report(self, message, level="INFO"):
        if not self.client:
            return
        try:
            await self.client.send_message(ADMIN_ID, f"🤖 **{level}**\n{message}")
        except:
            pass

    async def log_step(self, step_name, details, success=True):
        emoji = "✅" if success else "❌"
        msg = f"{emoji} **{step_name}**\n{details}"
        logger.info(msg)
        await self.send_report(msg, "STEP")

    async def log_error(self, error, context="", solution_hint=""):
        self.error_count += 1
        msg = f"❌ **ОШИБКА #{self.error_count}**\nКонтекст: {context}\nОшибка: {error}\n"
        if solution_hint:
            msg += f"💡 **Предлагаю:** {solution_hint}"
        logger.error(msg)
        await self.send_report(msg, "ERROR")

        if self.error_count >= self.max_errors:
            await self.send_report("🚨 **Достигнут лимит ошибок. Бот завершает работу.**", "CRITICAL")
            logger.critical("Достигнут лимит ошибок. Завершение работы.")
            sys.exit(1)

    async def suggest_fix(self, problem, solution_code):
        msg = f"🧠 **НЕОБХОДИМО ИЗМЕНИТЬ КОД**\nПроблема: {problem}\n\n```python\n{solution_code}\n```"
        await self.send_report(msg, "FIX SUGGESTION")

# ===== ОСНОВНАЯ ЛОГИКА =====
async def get_topic_ids(ai_logger):
    if not os.path.exists(SESSION_B64_FILE):
        await ai_logger.log_step("Проверка сессии", "Сессия не найдена!", False)
        return {}

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        await ai_logger.log_error(e, "Декодирование сессии", "Проверь корректность session.b64")
        return {}

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    ai_logger.client = client
    await ai_logger.log_step("Подключение к аккаунту", "Успешно", True)

    try:
        dialogs = await client.get_dialogs()
        target_dialog = None
        for dialog in dialogs:
            if dialog.id == TARGET_GROUP_ID:
                target_dialog = dialog
                break

        if not target_dialog:
            await ai_logger.log_step("Поиск группы", f"Группа {TARGET_GROUP_ID} не найдена", False)
            await client.disconnect()
            return {}

        topic_ids = {}
        if hasattr(target_dialog, 'forum_topics') and target_dialog.forum_topics:
            for topic in target_dialog.forum_topics:
                topic_ids[topic.title] = topic.id
            await ai_logger.log_step("Загрузка тем", f"Найдено {len(topic_ids)} тем", True)
        else:
            await ai_logger.log_step("Загрузка тем", "Группа не форум, темы отсутствуют", True)

        await client.disconnect()
        return topic_ids
    except Exception as e:
        await ai_logger.log_error(e, "Получение тем", "Проверь права доступа к группе")
        await client.disconnect()
        return {}

async def process_albums(limit=100):
    ai_logger = AILogger(None)
    await ai_logger.log_step("Запуск бота", f"Начинаю обработку {limit} сообщений", True)

    topic_ids = await get_topic_ids(ai_logger)

    if not os.path.exists(SESSION_B64_FILE):
        await ai_logger.log_step("Сессия", "Файл сессии отсутствует", False)
        return False

    try:
        with open(SESSION_B64_FILE, 'r') as f:
            b64_data = f.read().strip()
        decoded = base64.b64decode(b64_data)
        with open(SESSION_FILE, 'wb') as f:
            f.write(decoded)
        os.chmod(SESSION_FILE, 0o600)
    except Exception as e:
        await ai_logger.log_error(e, "Загрузка сессии", "Проверь права на файлы")
        return False

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    ai_logger.client = client
    await ai_logger.log_step("Подключение к аккаунту", "Успешно", True)

    try:
        channel = await client.get_entity(SOURCE_CHANNEL)
        await ai_logger.log_step("Подключение к каналу", f"Канал {SOURCE_CHANNEL} найден", True)
    except Exception as e:
        await ai_logger.log_error(e, "Получение канала", "Проверь правильность SOURCE_CHANNEL")
        await client.disconnect()
        return False

    albums = []
    history = await client(GetHistoryRequest(
        peer=channel,
        offset_id=0,
        offset_date=0,
        add_offset=0,
        max_id=0,
        min_id=0,
        hash=0,
        limit=limit
    ))

    await ai_logger.log_step("Получение истории", f"Получено {len(history.messages)} сообщений", True)

    i = 0
    while i < len(history.messages):
        msg = history.messages[i]
        if not msg.photo:
            i += 1
            continue
        group = [msg]
        j = i + 1
        while j < len(history.messages):
            nxt = history.messages[j]
            if nxt.photo and abs(nxt.date - msg.date).total_seconds() < 5:
                group.append(nxt)
                j += 1
            else:
                break
        if len(group) > 1:
            text = group[-1].message or ""
            photo_paths = set()
            for m in group:
                try:
                    p = await client.download_media(m, file=f"temp_{m.id}.jpg")
                    if p:
                        photo_paths.add(p)
                except:
                    pass
            if photo_paths:
                albums.append({"text": text, "photo_paths": list(photo_paths)})
        i = j

    await ai_logger.log_step("Обработка альбомов", f"Найдено {len(albums)} альбомов", True)
    await client.disconnect()

    if not albums:
        await ai_logger.log_step("Результат", "Альбомы не найдены", False)
        return True

    total_sent = 0
    for idx, album in enumerate(albums):
        text = replace_mentions(album["text"])
        topic = detect_topic(text)
        photos = album["photo_paths"]

        thread_id = topic_ids.get(topic) if topic_ids else None

        success = False
        for attempt in range(3):
            try:
                client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
                await client.connect()
                ai_logger.client = client
                group = await client.get_entity(TARGET_GROUP_ID)

                # === ОТПРАВКА ЧЕРЕЗ send_file (ПОДДЕРЖИВАЕТ parse_mode И ТЕМЫ) ===
                caption = f"📌 **{topic}**\n\n{text}" if text else None
                await client.send_file(
                    entity=group,
                    file=photos,
                    caption=caption,
                    parse_mode="markdown",
                    message_thread_id=thread_id
                )

                await ai_logger.log_step(f"Отправка альбома #{idx+1}", f"{len(photos)} фото в тему {topic}", True)
                total_sent += 1
                success = True
                await client.disconnect()
                break

            except Exception as e:
                await ai_logger.log_error(e, f"Попытка #{attempt+1} отправки", f"Ошибка: {e}")
                if attempt == 2:
                    await ai_logger.suggest_fix(
                        "SendMessageRequest не поддерживает parse_mode",
                        "Используй client.send_file() с caption и parse_mode"
                    )
                await client.disconnect()
                await asyncio.sleep(2)

        if not success:
            await ai_logger.send_report("🚫 **Альбом не отправлен после 3 попыток. Пропускаю.**", "WARNING")

    await ai_logger.log_step("Завершение", f"Обработано {total_sent} альбомов", True)
    await ai_logger.send_report("🎉 **Бот завершил работу!** Готов к следующему запуску.")
    return True

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
def detect_topic(text):
    TOPIC_MAP = {
        "prada": "Сумки PRADA",
        "ralph lauren": "Ralph Lauren",
        "gucci": "GUCCI",
        "fendi": "FENDI",
        "zimmermann": "ZIMMERMANN",
        "hermes": "Сумки Hermes",
        "chanel": "Chanel",
        "dior": "Сумки DIOR",
        "louis vuitton": "Сумки Louis Vuitton",
        "balenciaga": "BALENCIAGA",
        "loewe": "Сумки Loewe",
        "bottega veneta": "Сумки BOTTEGA VENETA",
        "givenchy": "GIVENCHY",
        "yves saint laurent": "Yves Saint Laurent",
        "miu miu": "Сумки MIU MIU",
        "the row": "Сумки THE ROW",
        "zegna": "Одежда Loro/Brunello/Kiton/Zegna",
        "loro piana": "Сумки Loro Piana",
        "brunello cucinelli": "Одежда Loro/Brunello/Kiton/Zegna",
        "acne studios": "Acne Studios",
        "maison margiela": "Сумки Maison Margiela",
        "lemaire": "Сумки LEMAIRE",
        "celine": "Сумки CELINE",
        "chrome hearts": "CHROME HEARTS",
        "moncler": "Moncler",
        "burberry": "BURBERRY",
        "canada goose": "CANADA GOOSE",
        "max mara": "Max Mara",
        "mcm": "Сумки MCM",
        "moynat": "Сумки MOYNAT PARIS",
        "юбка": "Женская одежда",
        "платье": "Женская одежда",
        "брюки": "Женская одежда",
        "шорты": "Женская одежда",
        "футболка": "Женская одежда",
        "рубашка": "Женская одежда",
        "топ": "Женская одежда",
        "куртка": "Зимние куртки",
        "пальто": "Пальто",
        "обувь": "Обувь Hermes",
        "кроссовки": "Кроссовки [LUXURY SNEAKERS]",
        "часы": "Часы",
        "ремень": "Ремни",
        "сумка": "Ассортимент",
        "очки": "Очки",
        "украшения": "Ювелирные украшения",
        "шапка": "Шарфы и шапки",
        "шарф": "Шарфы и шапки",
    }
    if not text:
        return "Ассортимент"
    text_lower = text.lower()
    if 'кроссовки' in text_lower: return "Кроссовки [LUXURY SNEAKERS]"
    if 'обувь' in text_lower: return "Обувь Hermes"
    if 'сумка' in text_lower: return "Сумки Hermes"
    for key, topic in TOPIC_MAP.items():
        if key in text_lower:
            return topic
    return "Ассортимент"

def replace_mentions(text):
    return re.sub(r'@\w+', MENTION_REPLACE, text)

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/health")
def health():
    asyncio.run(process_albums(limit=100))
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    asyncio.run(process_albums(limit=100))
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
