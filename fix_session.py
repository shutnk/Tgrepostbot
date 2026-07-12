import asyncio
import base64
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start(phone='+79030406091')
    
    # Получаем строку сессии
    session_str = client.session.save()
    
    # Кодируем в Base64 как текст
    b64_data = base64.b64encode(session_str.encode('utf-8')).decode('utf-8')
    
    # Сохраняем в файл
    with open('session.b64', 'w') as f:
        f.write(b64_data)
    
    print("✅ Сессия сохранена в session.b64 (в правильном формате)")
    await client.disconnect()

asyncio.run(main())
