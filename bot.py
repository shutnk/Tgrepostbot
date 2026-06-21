import threading
from flask import Flask
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHAT_ID = -1002414824426  # Поменяй это число на правильный ID группы!
TARGET_CHANNEL = "@trifferi097"

# Flask для бодрости
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is alive!", 200
threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000, threaded=True), daemon=True).start()

# Самый простой обработчик
async def forward_message(update, context):
    print(f"🔥 ПОЛУЧЕНО СООБЩЕНИЕ! Chat ID: {update.effective_chat.id}")
    
    if update.effective_chat.id == SOURCE_CHAT_ID:
        print("✅ Это наша группа!")
        if update.message:
            await update.message.copy(chat_id=TARGET_CHANNEL)
            print("✅ Переслано!")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, forward_message))
print("🚀 Тестовый бот запущен. Смотри логи Render!")
app.run_polling(allowed_updates=['message', 'channel_post'])
