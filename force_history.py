import asyncio
import re
from telegram import Bot

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"
TARGET_CHANNEL = "@trifferi02"
NEW_AUTHOR = "@esen_baevich"

bot = Bot(token=BOT_TOKEN)

async def force_catch_up():
    print("⏳ Принудительное получение всей истории...")
    
    # Сбрасываем оффсет до 0 (бот думает, что никогда не работал)
    # Это заставит Telegram отдать ВСЕ посты с самого первого дня
    await bot.get_updates(offset=0, limit=1)
    
    # Теперь включаем полноценный режим сбора
    offset_id = 0
    count = 0
    
    while True:
        try:
            updates = await bot.get_updates(offset=offset_id, limit=100, timeout=30)
            
            if not updates:
                print("✅ Все посты получены!")
                break
            
            for update in updates:
                offset_id = update.update_id + 1
                
                if update.channel_post:
                    msg = update.channel_post
                    if msg.chat.username.replace("@", "") != SOURCE_CHANNEL.replace("@", ""):
                        continue
                    
                    text = msg.text or msg.caption or ""
                    new_text = re.sub(r'@\w+', NEW_AUTHOR, text)
                    
                    try:
                        if msg.photo:
                            await bot.send_photo(
                                chat_id=TARGET_CHANNEL,
                                photo=msg.photo[-1].file_id,
                                caption=new_text[:1024] if new_text else None
                            )
                        elif msg.video:
                            await bot.send_video(
                                chat_id=TARGET_CHANNEL,
                                video=msg.video.file_id,
                                caption=new_text[:1024] if new_text else None
                            )
                        elif msg.text:
                            await bot.send_message(
                                chat_id=TARGET_CHANNEL,
                                text=new_text
                            )
                        else:
                            await msg.copy(chat_id=TARGET_CHANNEL)
                            
                        count += 1
                        print(f"✅ Скопирован пост #{count}")
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")
                        
                    await asyncio.sleep(1)
                    
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            break
    
    print(f"🎉 Готово! Всего скопировано: {count} постов.")

async def main():
    await force_catch_up()

if __name__ == "__main__":
    asyncio.run(main())
