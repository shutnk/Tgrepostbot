from telethon import TelegramClient
import asyncio

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'
PHONE = '+79030406091'
PASSWORD = 'nurbek2002'

async def main():
    client = TelegramClient('session', API_ID, API_HASH)
    await client.connect()
    print("✅ Подключено!")
    
    if not await client.is_user_authorized():
        print("📱 Отправляю запрос кода (он придёт в Telegram)...")
        await client.send_code_request(PHONE)
        code = input("📝 Введи код из Telegram: ")
        try:
            await client.sign_in(PHONE, code)
        except:
            print("🔐 Ввожу твой пароль...")
            await client.sign_in(password=PASSWORD)
    
    print("✅ Вход выполнен! Сессия сохранена.")
    await client.disconnect()

asyncio.run(main())
