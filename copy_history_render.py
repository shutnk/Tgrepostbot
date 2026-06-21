import asyncio
import re
from telegram import Bot

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"
TARGET_CHANNEL = "@trifferi02"

async def copy_posts():
    print("🚀 Сбрасываю память бота...")
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # Сбрасываем offset (бот забывает всё, что видел раньше)
        await bot.get_updates(offset=0, limit=1)
        
        # Теперь получаем всё, что есть в истории
        print("📥 Загружаю посты...")
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
