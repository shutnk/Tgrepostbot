import asyncio
import re
from telethon import TelegramClient, events
import threading
import http.server

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
TARGET_CHANNEL = "@trifferi11"
NEW_AUTHOR = "@esen_baevich"
# ==============================================

# Фейковый сервер, чтобы Render не убивал процесс
def run_fake_server():
    server = http.server.HTTPServer(("0.0.0.0", 10000), http.server.BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# Клиент Telethon
client = TelegramClient('bot_session', api_id=2040, api_hash='b18441a1ff607e10a989891a5462e627')

# Буфер для ручного режима
pending_posts = {}

@client.on(events.NewMessage)
async def handle_forward(event):
    msg = event.message
    if not msg:
        return
    user_id = msg.sender_id
    
    # Если команда "Из темы: ..."
    if msg.text and msg.text.startswith("Из темы:"):
        topic_name = msg.text.replace("Из темы:", "").strip()
        pending_posts[user_id] = {"topic": topic_name, "files": []}
        await msg.reply(f"✅ Тема '{topic_name}' выбрана! Отправь пост.")
        return
    
    # Если активная тема
    if user_id in pending_posts:
        topic_name = pending_posts[user_id]["topic"]
        
        if msg.photo:
            pending_posts[user_id]["files"].append(msg.photo[-1].id)
            return
        
        if msg.text:
            caption = re.sub(r'@\w+', NEW_AUTHOR, msg.text)
            await asyncio.sleep(2)
            
            files = pending_posts[user_id]["files"]
            if files:
                # Отправляем альбом в тему канала
                await client.send_file(
                    TARGET_CHANNEL,
                    files,
                    caption=caption,
                    message_thread_id=topic_name
                )
                await msg.reply(f"✅ Альбом в тему '{topic_name}'!")
            else:
                await client.send_message(
                    TARGET_CHANNEL,
                    caption,
                    message_thread_id=topic_name
                )
            del pending_posts[user_id]

async def main():
    print("🚀 Бот на Telethon запущен! Жду команды 'Из темы:'...")
    await client.start(bot_token=BOT_TOKEN)
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
