import asyncio
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHAT_ID = -1002433118546   # @trifferi098
TARGET_CHAT_ID = -1002365330617   # @trifferi097

async def forward_message(update, context):
    if update.channel_post and update.channel_post.chat_id == SOURCE_CHAT_ID:
        await update.channel_post.copy(chat_id=TARGET_CHAT_ID)
        print("✅ Переслано!")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.Chat(SOURCE_CHAT_ID) & filters.ChatType.CHANNEL, forward_message))
print("🚀 Бот запущен, ждём посты...")
app.run_polling(allowed_updates=['channel_post'])
