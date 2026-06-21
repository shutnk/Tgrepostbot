import asyncio
import threading
import re
import sqlite3
from datetime import datetime
from flask import Flask
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
TARGET_CHANNEL = "@trifferi11"
NEW_AUTHOR = "@esen_baevich"
# ==============================================

# ===== Flask =====
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is alive!", 200
threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000, threaded=True), daemon=True).start()

# ===== Обработчик входящих сообщений от тебя =====
async def handle_forward(update, context):
    if update.message and update.message.text:
        text = update.message.text
        
        # Если сообщение начинается с "Из темы:" — это команда
        if text.startswith("Из темы:"):
            try:
                # Извлекаем название темы (всё после двоеточия до конца строки)
                topic_name = text.replace("Из темы:", "").strip()
                
                # Бот создаёт тему (если нет) и отправляет туда это сообщение
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=f"📦 Пост из темы: {topic_name}\n\n{update.message.text}",
                    message_thread_id=topic_name
                )
                await update.message.reply_text(f"✅ Пост отправлен в тему '{topic_name}'!")
                print(f"✅ Пост отправлен в тему: {topic_name}")
                
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}")
                print(f"❌ Ошибка: {e}")
        
        else:
            # Если это обычное сообщение (без команды) — пересылаем в General
            await update.message.copy(chat_id=TARGET_CHANNEL)
            await update.message.reply_text("✅ Сообщение отправлено в General.")

# ===== Запуск =====
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_forward))

print("🚀 Бот готов! Жду сообщения с командой 'Из темы: Название'.")
app.run_polling(allowed_updates=['message'])
