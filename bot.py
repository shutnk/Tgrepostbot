import os
import time
import requests
import logging

# === НАСТРОЙКИ ===
TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = "@trifferi_katalog"

# === СПИСОК ТЕМ (оригинальный, без эмодзи в названии) ===
TOPICS = [
    "Часы", "Сумки Hermes", "Обувь Hermes", "Ремень Hermes", "Сумки CHANEL",
    "Женская одежда", "Сумки THE ROW", "Chanel", "Сумки MIU MIU", "Одежда для детей",
    "Сумки PRADA", "CHROME HEARTS", "Женская обувь", "Сумки YSL",
    "Женская верхняя одежда (Кожа, кашемир)", "Ремни", "Шарфы и шапки",
    "Одежда Loro/Brunello/Kiton/Zegna", "Очки", "Украшения Schiaparelli",
    "Сумки Schiaparelli", "Dolce&Gabbana", "Мужская верхняя одежда",
    "Купальники и пляжная одежда", "Сумки Loewe", "Сумки Loro Piana",
    "Сумки BOTTEGA VENETA", "Классическая мужская обувь", "Сумки Louis Vuitton",
    "ZIMMERMANN", "EXCLUSIVE", "Ralph Lauren", "BALENCIAGA", "FENDI", "GUCCI",
    "Сумки Jacquemus", "Сумки BALENCIAGA", "Кроссовки Louis Vuitton",
    "Кроссовки [LUXURY SNEAKERS]", "Сумки DIOR", "Сумки GOYARD", "Мужские сумки",
    "Чемоданы и дорожные сумки", "Сумки BVLGARI", "Сумки Manolo Blahnik",
    "Обувь Alaïa", "BURBERRY", "Moncler", "Обвесы на сумку", "Кроссовки BALENCIAGA",
    "Обувь Chanel", "Обувь для пляжа и бассейна", "Женские сапоги",
    "Обувь Loro/Brunello/Kiton/Zegna", "Acne Studios",
    "CHROME HEARTS Украшения из серебра", "Сумки Chrome Hearts", "Товары для дома",
    "Сумки CELINE", "Лоферы Loro Piana", "Сумки Maison Margiela", "Сумки Acne Studios",
    "Сумки LEMAIRE", "Украшения (бижутерия)", "CANADA GOOSE", "Yves Saint Laurent",
    "AMI Paris", "Кроссовки LOEWE", "Кроссовки GUCCI", "Arcteryx", "GIVENCHY",
    "Классическая мужская одежда", "MAISON MARGIELA", "WELLDONE", "AMIRI",
    "Женская обувь II", "Сумки Roger Vivier", "Сумки Dolce Gabbana", "Сумки Alaïa",
    "Зимние куртки", "Обувь для детей",
    "Классическая мужская обувь из экзотической кожи", "Сумки Ralph Lauren",
    "Сумки MCM", "Max Mara", "Ассортимент", "Пальто", "alexander wang",
    "ENFANTS RICHES DEPRIMES", "Ювелирные украшения", "Обувь Louis Vuitton",
    "Сумки MOYNAT PARIS"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_first_message(chat_id, topic_id):
    """Отправляет первое сообщение в тему, чтобы Telegram создал иконку-букву"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "message_thread_id": topic_id,
        "text": "👋 Добро пожаловать в тему!"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

def create_topic(name):
    url = f"https://api.telegram.org/bot{TOKEN}/createForumTopic"
    payload = {
        "chat_id": CHAT_ID,
        "name": name
    }
    try:
        resp = requests.post(url, data=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            # Достаём ID созданной темы
            topic_id = data["result"]["message_thread_id"]
            # Сразу отправляем первое сообщение, чтобы появилась буква-иконка
            send_first_message(CHAT_ID, topic_id)
            return True, None
        error = data.get("description", "")
        if "TOPIC_NAME_OCCUPIED" in error or "already exists" in error:
            return True, "exists"
        return False, error
    except Exception as e:
        return False, str(e)

def main():
    logger.info("🚀 Начинаю создание тем (с паузами для избежания лимитов)...")
    created = 0; skipped = 0; errors = 0
    total = len(TOPICS)

    for idx, name in enumerate(TOPICS, 1):
        success, msg = create_topic(name)
        if success and msg == "exists":
            logger.info(f"➖ [{idx}/{total}] Пропущено (уже есть): {name}")
            skipped += 1
        elif success:
            logger.info(f"✅ [{idx}/{total}] Создано + отправлено приветствие: {name}")
            created += 1
        else:
            logger.info(f"❌ [{idx}/{total}] Ошибка: {name} — {msg}")
            errors += 1
        
        # Ждём 3 секунды между темами, чтобы Telegram не банил
        time.sleep(3)

    logger.info(f"🏁 ЗАВЕРШЕНО. Создано: {created}, Пропущено: {skipped}, Ошибок: {errors}")

if __name__ == "__main__":
    main()
