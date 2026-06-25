import asyncio
import re
import time
import sqlite3
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateForumTopicRequest, GetFullChannelRequest
from telethon.errors import FloodWaitError

# ================= НАСТРОЙКИ =================
SOURCE_CHANNEL = "@blvckrooom"
DEST_CHANNEL = "@trifferi02"
OWNER_USERNAME = "nurikadambol"
OLD_USERNAMES = ["blvckrooom", "thesameseven"]

DB_PATH = "copied.db"
# ==============================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS copied (
            source_id INTEGER PRIMARY KEY,
            topic_name TEXT,
            copied_at TEXT
        )
    """)
    conn.commit()
    return conn

db = init_db()

async def copy_all():
    print("🔥 Копирование через MTProxy...")
    
    # Используем публичный MTProxy (обход блокировок)
    client = TelegramClient(
        'session',
        api_id=2040,
        api_hash='b18441a1ff607e10a989891a5462e627',
        proxy=('http', '51.15.164.90', 3128)
    )
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Вход выполнен! Ты онлайн как {me.first_name}")
    
    source = await client.get_entity(SOURCE_CHANNEL)
    dest = await client.get_entity(DEST_CHANNEL)
    
    print(f"📥 Начинаю копирование всех постов из {SOURCE_CHANNEL}...")
    count = 0
    
    async for msg in client.iter_messages(source, limit=None):
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM copied WHERE source_id = ?", (msg.id,))
        if cursor.fetchone():
            continue
        
        if not msg.text and not msg.media:
            continue
        
        # Определяем тему
        topic_name = "General"
        try:
            if msg.reply_to and hasattr(msg.reply_to, 'forum_topic_id'):
                channel_full = await client(GetFullChannelRequest(source))
                for topic in channel_full.forum_topics:
                    if topic.id == msg.reply_to.forum_topic_id:
                        topic_name = topic.title
                        break
        except:
            pass
        
        # Заменяем @ники
        text = msg.text or msg.caption or ""
        new_text = re.sub(rf'@\w+', f'@{OWNER_USERNAME}', text)
        
        # Создаём тему в целевом канале (если нет)
        topic_id = None
        try:
            new_topic = await client(CreateForumTopicRequest(
                channel=dest,
                title=topic_name
            ))
            topic_id = new_topic.id
            print(f"✅ Тема '{topic_name}' создана!")
        except:
            pass
        
        try:
            if msg.photo:
                if hasattr(msg, 'grouped_id') and msg.grouped_id:
                    group_msgs = await client.get_messages(source, limit=10, max_id=msg.id)
                    media_files = [g.photo[-1].file_id for g in group_msgs if g.photo]
                    await client.send_file(dest, media_files, caption=new_text, reply_to=topic_id)
                else:
                    await client.send_file(dest, msg.photo[-1].file_id, caption=new_text, reply_to=topic_id)
            elif msg.video:
                await client.send_file(dest, msg.video.file_id, caption=new_text, reply_to=topic_id)
            elif msg.text:
                await client.send_message(dest, new_text, reply_to=topic_id)
            else:
                await client.send_message(dest, msg, reply_to=topic_id)
            
            cursor.execute("INSERT INTO copied (source_id, topic_name, copied_at) VALUES (?, ?, ?)",
                          (msg.id, topic_name, time.strftime("%Y-%m-%d %H:%M:%S")))
            db.commit()
            count += 1
            print(f"✅ Пост #{msg.id} скопирован в тему '{topic_name}'")
            await asyncio.sleep(2)
            
        except FloodWaitError as e:
            print(f"⏳ Ожидание {e.seconds}с...")
            await asyncio.sleep(e.seconds)
    
    print(f"🎉 Готово! Всего скопировано {count} постов.")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(copy_all())
