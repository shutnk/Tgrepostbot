import threading
from flask import Flask
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
TARGET_CHANNEL = "@trifferi097"

# Flask-сервер для бодрости
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is alive!", 200
threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000, threaded=True), daemon=True).start()

async def forward_message(update, context):
    # Эта строчка напечатает ВСЁ, что приходит боту, прямо в логи Render
    print(f"🔥🔥🔥 ЧТО-ТО ПРИШЛО! Chat ID: {update.effective_chat.id}")
    
    # Если пришло сообщение, пересылаем его
    if update.message:
        await update.message.copy(chat_id=TARGET_CHANNEL)
        print("✅ УСПЕШНО ПЕРЕСЛАНО!")

# Запускаем бота
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, forward_message))
print("🚀 Бот запущен! Жду сообщений...")
app.run_polling(allowed_updates=['message', 'channel_post'])
