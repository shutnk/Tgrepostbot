import os
import time
import requests
import logging

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = -1003991874844

# Твой Mini App URL (создай его через @BotFather -> /newapp)
MINI_APP_URL = "https://t.me/trifferi_katalog/app"  # Пример, замени на свой

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

def create_topic(name):
    url = f"https://api.telegram.org/bot{TOKEN}/createForumTopic"
    payload = {"chat_id": CHAT_ID, "name": name}
    try:
        resp = requests.post(url, data=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            return True, data["result"]["message_thread_id"]
        error = data.get("description", "")
        if "TOPIC_NAME_OCCUPIED" in error or "already exists" in error:
            return True, None
        return False, error
    except Exception as e:
        return False, str(e)

def send_icon_button(chat_id, topic_id, topic_name):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Кнопка открывает Mini App для выбора иконки
    keyboard = {
        "inline_keyboard": [[{
            "text": "⚡️ Выбрать иконку",
            "web_app": {"url": f"{MINI_APP_URL}?topic={topic_name}&id={topic_id}"}
        }]]
    }
    payload = {
        "chat_id": chat_id,
        "message_thread_id": topic_id,
        "text": f"✅ Тема «{topic_name}» создана!\nНажми кнопку ниже, чтобы поставить анимированную иконку:",
        "reply_markup": keyboard
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

def main():
    logger.info("🚀 Создаю чистые темы + кнопки для иконок...")
    created = 0

    for idx, name in enumerate(TOPICS, 1):
        success, topic_id = create_topic(name)
        if success and topic_id:
            logger.info(f"✅ [{idx}] Создано: {name} (ID: {topic_id})")
            send_icon_button(CHAT_ID, topic_id, name)
            created += 1
            time.sleep(3)
        elif success and not topic_id:
            logger.info(f"➖ [{idx}] Пропущено (уже есть): {name}")
        else:
            logger.error(f"❌ [{idx}] Ошибка: {name}")

    logger.info(f"🏁 Готово. Создано: {created}")

if __name__ == "__main__":
    main()
