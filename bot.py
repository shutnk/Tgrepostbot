import asyncio
import re
import time
import sqlite3
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateForumTopicRequest
from telethon.errors import FloodWaitError

# ================= НАСТРОЙКИ =================
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

# ВАЖНО: Используем ID, который ты получил (с -100 в начале)
SOURCE_CHANNEL_ID = -1002028675800

DEST_CHANNEL = "@trifferi02"
OWNER_USERNAME = "nurikadambol"

# Прокси (проверенный)
PROXY = ('http', '51.15.164.90', 3128)

DB_PATH = "posted.db"
# ==============================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posted_messages (
            source_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    return conn

db = init_db()

def is_posted(source_id):
    row = db.execute("SELECT 1 FROM posted_messages WHERE source_id = ?", (source_id,)).fetchone()
    return row is not None

def mark_posted(source_id):
    db.execute("INSERT OR IGNORE INTO posted_messages (source_id) VALUES (?)", (source_id,))
    db.commit()

async def main():
    print("🚀 Запуск с фиксированным ID канала...")
    
    client = TelegramClient('session', API_ID, API_HASH, proxy=PROXY)
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Вход выполнен! Ты онлайн как {me.first_name}")
    
    # Используем числовой ID вместо имени
    try:
        source = await client.get_entity(SOURCE_CHANNEL_ID)
        print(f"✅ Канал получен через ID: {SOURCE_CHANNEL_ID}")
    except Exception as e:
        print(f"❌ Ошибка получения канала по ID: {e}")
        print("⚠️ Пробуем получить через имя как запасной вариант...")
        source = await client.get_entity("@blvckrooom")
    
    dest = await client.get_entity(DEST_CHANNEL)
    
    print(f"📥 Слежу за каналом -> {DEST_CHANNEL}")
    print("⏳ Жду новые посты...")
    
    last_id = 0
    while True:
        try:
            messages = await client.get_messages(source, limit=5, min_id=last_id)
            for msg in reversed(messages):
                if msg.id <= last_id or is_posted(msg.id):
                    continue
                
                # Определяем тему
                text = msg.text or msg.caption or ""
                topic_name = "General"
                
                hashtag = re.search(r'#(\w+)', text)
                if hashtag:
                    topic_name = hashtag.group(1)
                elif "сумка" in text.lower():
                    topic_name = "Сумки"
                elif "обувь" in text.lower():
                    topic_name = "Обувь"
                elif "куртка" in text.lower():
                    topic_name = "Куртки"
                
                # Создаём тему
                topic_id = None
                try:
                    new_topic = await client(CreateForumTopicRequest(
                        channel=dest,
                        title=topic_name
                    ))
                    topic_id = new_topic.id
                    print(f"✅ Тема '{topic_name}' создана!")
                except Exception:
                    print(f"⚠️ Тема '{topic_name}' уже есть. Отправляю в General.")
                
                try:
                    # Пересылаем сообщение
                    await client.forward_messages(
                        DEST_CHANNEL,
                        messages=msg.id,
                        from_peer=source,
                        message_thread_id=topic_id
                    )
                    
                    mark_posted(msg.id)
                    print(f"✅ Пост #{msg.id} скопирован в тему '{topic_name}'!")
                    
                except FloodWaitError as e:
                    print(f"⏳ Ожидание {e.seconds}с...")
                    await asyncio.sleep(e.seconds)
                
                await asyncio.sleep(2)
            
            if messages:
                last_id = messages[0].id
            
            await asyncio.sleep(10)
        
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен.")
