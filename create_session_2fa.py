import asyncio
import base64
from telethon import TelegramClient

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'

async def main():
    client = TelegramClient('nurik_session_2fa', API_ID, API_HASH)
    
    # Вход с запросом 2FA
    await client.start(phone='+79030406091')
    
    print("✅ Сессия создана!")
    
    with open('nurik_session_2fa.session', 'rb') as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')
    
    with open('session.b64', 'w') as f:
        f.write(b64_data)
    
    print("✅ Файл session.b64 сохранён!")
    await client.disconnect()

asyncio.run(main())
