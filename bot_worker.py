import asyncio
import re
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
TARGET_CHANNEL = "@trifferi11"
NEW_AUTHOR = "@esen_baevich"

pending_posts = {}

async def handle_forward(update, context):
    if update.message:
        msg = update.message
        user_id = msg.from_user.id
        
        if msg.text and msg.text.startswith("Из темы:"):
            topic_name = msg.text.replace("Из темы:", "").strip()
            pending_posts[user_id] = {"topic": topic_name, "files": []}
            await msg.reply_text(f"✅ Тема '{topic_name}' выбрана! Отправь пост.")
            return
        
        if user_id in pending_posts:
            topic_name = pending_posts[user_id]["topic"]
            if msg.photo:
                pending_posts[user_id]["files"].append(msg.photo[-1].file_id)
                return
            if msg.text:
                caption = re.sub(r'@\w+', NEW_AUTHOR, msg.text)
                await asyncio.sleep(2)
                files = pending_posts[user_id]["files"]
                if files:
                    media_group = [InputMediaPhoto(media=fid) for fid in files]
                    await context.bot.send_media_group(
                        chat_id=TARGET_CHANNEL,
                        media=media_group,
                        caption=caption,
                        message_thread_id=topic_name
                    )
                    await msg.reply_text(f"✅ Альбом в тему '{topic_name}'!")
                else:
                    await context.bot.send_message(
                        chat_id=TARGET_CHANNEL,
                        text=caption,
                        message_thread_id=topic_name
                    )
                del pending_posts[user_id]

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_forward))
    print("🚀 Бот-воркер запущен! Жду команды...")
    await app.run_polling(allowed_updates=['message'])

if __name__ == "__main__":
    asyncio.run(main())
