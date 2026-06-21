import asyncio
import re
from telegram import Bot

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"
TARGET_CHANNEL = "@trifferi02"

async def copy_posts():
    print("🚀 Начинаю копирование через бота (прямо на сервере)...")
    bot = Bot(token=BOT_TOKEN)
    
    try:
        updates = await bot.get_updates(limit=100)
        count = 0
        for u in updates:
            if u.channel_post:
                msg = u.channel_post
                if msg.chat.username == SOURCE_CHANNEL.replace("@", ""):
                    new_text = re.sub(r'@\w+', '@esen_baevich', msg.caption or msg.text or "")
                    await msg.copy(chat_id=TARGET_CHANNEL, caption=new_text)
                    count += 1
                    print(f"✅ Скопирован пост {count}")
        print(f"🎉 Готово! Скопировано {count} постов.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(copy_posts())
