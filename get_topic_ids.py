import asyncio
import base64
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
SESSION_B64_FILE = 'session.b64'

async def main():
    with open(SESSION_B64_FILE, 'r') as f:
        b64_data = f.read().strip()
    decoded = base64.b64decode(b64_data).decode('utf-8')
    session = StringSession(decoded)
    
    client = TelegramClient(session, API_ID, API_HASH)
    await client.connect()
    
    group = await client.get_entity(-1003991874844)
    print(f"✅ Группа: {group.title} (ID: {group.id})")
    
    # Получаем сообщения из группы
    messages = await client.get_messages(group, limit=10)
    
    print("\n📌 Найденные темы (ID):")
    for msg in messages:
        if msg.reply_to and msg.reply_to.forum_topic:
            print(f"  • Тема: {msg.reply_to.forum_topic.title} (ID: {msg.reply_to.forum_topic.id})")
    
    await client.disconnect()

asyncio.run(main())
