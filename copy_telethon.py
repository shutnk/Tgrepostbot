import asyncio
import re
from telethon import TelegramClient

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"
TARGET_CHANNEL = "@trifferi02"
NEW_AUTHOR = "@esen_baevich"

# Стандартные ключи для ботов (работают всегда)
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
# ==============================================

async def copy_history():
    print("⏳ Начинаю копирование истории через Telethon (стандартный API)...")
    
    client = TelegramClient('session', api_id=API_ID, api_hash=API_HASH)
    
    try:
        await client.start(bot_token=BOT_TOKEN)
        
        source = await client.get_entity(SOURCE_CHANNEL)
        target = await client.get_entity(TARGET_CHANNEL)
        
        print(f"✅ Источник: {SOURCE_CHANNEL}")
        print(f"✅ Приёмник: {TARGET_CHANNEL}")
        
        count = 0
        async for msg in client.iter_messages(source, limit=1000):
            if not msg.text and not msg.caption and not msg.photo and not msg.video:
                continue
            
            text = msg.text or msg.caption or ""
            new_text = re.sub(r'@\w+', NEW_AUTHOR, text)
            
            try:
                if msg.photo:
                    await client.send_file(target, msg.photo, caption=new_text[:1024] if new_text else None)
                elif msg.video:
                    await client.send_file(target, msg.video, caption=new_text[:1024] if new_text else None)
                elif msg.text:
                    await client.send_message(target, new_text)
                else:
                    await client.send_message(target, msg)
                    
                count += 1
                print(f"✅ Скопирован пост #{count}")
            except Exception as e:
                print(f"❌ Ошибка копирования: {e}")
            
            await asyncio.sleep(1)
        
        print(f"🎉 Готово! Скопировано {count} постов.")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(copy_history())
