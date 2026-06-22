import asyncio
import re
import threading
import http.server
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
TARGET_CHANNEL = "@trifferi11"
NEW_AUTHOR = "@esen_baevich"
# ==============================================

# Фейковый сервер для Render
def run_fake_server():
    server = http.server.HTTPServer(("0.0.0.0", 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Буфер для ручного режима
pending_posts = {}

@dp.message()
async def handle_forward(message: types.Message):
    user_id = message.from_user.id
    
    # Команда "Из темы: ..."
    if message.text and message.text.startswith("Из темы:"):
        topic_name = message.text.replace("Из темы:", "").strip()
        pending_posts[user_id] = {"topic": topic_name, "files": []}
        await message.reply(f"✅ Тема '{topic_name}' выбрана! Отправь пост.")
        return
    
    # Если активная тема
    if user_id in pending_posts:
        topic_name = pending_posts[user_id]["topic"]
        
        if message.photo:
            pending_posts[user_id]["files"].append(message.photo[-1].file_id)
            return
        
        if message.text:
            caption = re.sub(r'@\w+', NEW_AUTHOR, message.text)
            await asyncio.sleep(2)
            
            files = pending_posts[user_id]["files"]
            if files:
                media_group = [InputMediaPhoto(media=fid) for fid in files]
                await bot.send_media_group(
                    chat_id=TARGET_CHANNEL,
                    media=media_group,
                    caption=caption,
                    message_thread_id=topic_name
                )
                await message.reply(f"✅ Альбом отправлен в тему '{topic_name}'!")
            else:
                await bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=caption,
                    message_thread_id=topic_name
                )
            del pending_posts[user_id]

# Запуск бота
async def main():
    print("🚀 Бот на aiogram запущен! Жду команды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
