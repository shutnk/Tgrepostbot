import requests
import time
import sys

BOT_TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"

print("🚀 ТЕСТ: Прямой запрос к Telegram API...")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
try:
    resp = requests.get(url, timeout=20)
    print(f"✅ HTTP Статус: {resp.status_code}")
    print(f"📦 JSON Ответ: {resp.json()}")
except Exception as e:
    print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")

print("✅ ТЕСТ ЗАВЕРШЁН")
