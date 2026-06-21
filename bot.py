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
SOURCE_CHANNEL = "@blvckrooom"           # Откуда берём
TARGET_CHANNEL = "@trifferi11"           # Куда отправляем (теперь сюда!)
NEW_AUTHOR = "@esen_baevich"

DB_NAME = "posted_messages.db"
# ==============================================

# ===== Flask =====
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is alive!", 200
threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000, threaded=True), daemon=True).start()

# ===== База данных =====
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posted (
            source_id INTEGER PRIMARY KEY,
            target_id INTEGER,
            source_chat_id INTEGER,
            posted_at TEXT
        )
    """)
    conn.commit()
    return conn

db = init_db()

def is_posted(source_msg_id, source_chat_id):
    cursor = db.cursor()
    cursor.execute(
        "SELECT 1 FROM posted WHERE source_id = ? AND source_chat_id = ?",
        (source_msg_id, source_chat_id)
    )
    return cursor.fetchone() is not None

def save_posted(source_msg_id, target_msg_id, source_chat_id):
    cursor = db.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO posted VALUES (?, ?, ?, ?)",
        (source_msg_id, target_msg_id, source_chat_id, datetime.now().isoformat())
    )
    db.commit()

# ===== Обработчик ссылок =====
async def handle_link(update, context):
    if update.message and update.message.text:
        text = update.message.text
        if 't.me/' in text and '|' in text:
            try:
                parts = text.split(' | ')
                link = parts[0]
                topic_name = parts[1]
                
                msg_id = int(link.split('/')[-1])
                
                source_chat = await context.bot.get_chat(SOURCE_CHANNEL)
                if is_posted(msg_id, source_chat.id):
                    await update.message.reply_text(f"⏭️ Пост {msg_id} уже скопирован.")
                    return

                # Получаем сообщение (бота должны быть админом в SOURCE_CHANNEL)
                msg = await context.bot.get_message(chat_id=SOURCE_CHANNEL, message_id=msg_id)
                
                new_text = re.sub(r'@\w+', NEW_AUTHOR, msg.caption or msg.text or "")
                
                # ===== СОЗДАНИЕ ТЕМЫ И ОТПРАВКА =====
                try:
                    sent_msg = await msg.copy(
                        chat_id=TARGET_CHANNEL,
                        caption=new_text,
                        message_thread_id=topic_name
                    )
                except Exception:
                    # Если темы нет — создаём её
                    await context.bot.create_forum_topic(
                        chat_id=TARGET_CHANNEL,
                        name=topic_name
                    )
                    sent_msg = await msg.copy(
                        chat_id=TARGET_CHANNEL,
                        caption=new_text,
                        message_thread_id=topic_name
                    )
                
                save_posted(msg_id, sent_msg.message_id, source_chat.id)
                
                await update.message.reply_text(f"✅ Пост {msg_id} в тему '{topic_name}'!")
                print(f"✅ Пост {msg_id} в тему '{topic_name}'")
                
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}")
                print(f"❌ Ошибка: {e}")

# ===== Запуск =====
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

print("🚀 Бот готов! Создаёт темы в @trifferi11 и загружает посты.")
app.run_polling(allowed_updates=['message'])
