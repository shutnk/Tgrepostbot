import requests
import time

BOT_TOKEN = "8927033296:AAGa4W-EJma1UzbNzVUSKjn2vNsM57FB7R8"
SOURCE_CHANNEL = "@blvckrooom"

def tg_request(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, data=data, timeout=30)
        return resp.json()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def main():
    print("🚀 Принудительная подписка бота на канал...")
    
    # 1. Пингуем канал, чтобы бот «узнал» о нём
    info = tg_request("getChat", {"chat_id": SOURCE_CHANNEL})
    if info and info.get("ok"):
        print(f"✅ Бот распознал канал: {info['result']['title']}")
    else:
        print("❌ Бот не может распознать канал. Проверь, подписан ли бот.")
        return
    
    # 2. Сбрасываем offset (заставляем бота «забыть» старые посты)
    tg_request("getUpdates", {"offset": 0, "limit": 1})
    time.sleep(2)
    
    print("✅ Бот готов к сбору постов. Теперь запусти `copy_history.py`")

if __name__ == "__main__":
    main()
