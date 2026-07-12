import asyncio
import base64
import os
from telethon import TelegramClient

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'

async def main():
    client = TelegramClient('nurik_session', API_ID, API_HASH)
    await client.start()
    print("✅ Сессия создана!")
    
    with open('nurik_session.session', 'rb') as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Записываем в файл session.b64
    with open('session.b64', 'w') as f:
        f.write(b64_data)
    
    print("✅ Файл session.b64 сохранён!")
    os.remove('nurik_session.session')
    print("✅ Временный файл удалён.")
    await client.disconnect()

asyncio.run(main())
