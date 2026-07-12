import asyncio
import base64
import os
from telethon import TelegramClient

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'

async def main():
    # Используем уникальное имя файла, чтобы точно не пересечься со старыми
    client = TelegramClient('clean_2026_session', API_ID, API_HASH)
    await client.start(phone='+79030406091')
    print("✅ Новая чистая сессия создана!")
    
    with open('clean_2026_session.session', 'rb') as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')
    
    with open('session.b64', 'w') as f:
        f.write(b64_data)
    
    print("✅ Файл session.b64 сохранён!")
    os.remove('clean_2026_session.session')
    await client.disconnect()

asyncio.run(main())
