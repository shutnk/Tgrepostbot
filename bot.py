import os
import time
import requests
import logging

# === НАСТРОЙКИ ===
TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = "@trifferi_katalog"

# === ОФИЦИАЛЬНЫЕ ID АНИМИРОВАННЫХ ИКОНОК (работают у админов) ===
ICON_MAP = {
    "Часы": "5385654382486539496",
    "Сумки Hermes": "5385754022216923412",
    "Обувь Hermes": "5385729374944167175",
    "Ремень Hermes": "5385785779086361281",
    "Сумки CHANEL": "5385754022216923412",
    "Женская одежда": "5385707592904087822",
    "Сумки THE ROW": "5385754022216923412",
    "Chanel": "5385754022216923412",
    "Сумки MIU MIU": "5385754022216923412",
    "Одежда для детей": "5385783281911921219",
    "Сумки PRADA": "5385754022216923412",
    "CHROME HEARTS": "5385647869870530128",
    "Женская обувь": "5385736843026391346",
    "Сумки YSL": "5385754022216923412",
    "Женская верхняя одежда (Кожа, кашемир)": "5385707592904087822",
    "Ремни": "5385785779086361281",
    "Шарфы и шапки": "5385759624885116002",
    "Одежда Loro/Brunello/Kiton/Zegna": "5385713080715649102",
    "Очки": "5385685000368160908",
    "Украшения Schiaparelli": "5385647869870530128",
    "Сумки Schiaparelli": "5385754022216923412",
    "Dolce&Gabbana": "5385754022216923412",
    "Мужская верхняя одежда": "5385713080715649102",
    "Купальники и пляжная одежда": "5385819370870144587",
    "Сумки Loewe": "5385754022216923412",
    "Сумки Loro Piana": "5385754022216923412",
    "Сумки BOTTEGA VENETA": "5385754022216923412",
    "Классическая мужская обувь": "5385729374944167175",
    "Сумки Louis Vuitton": "5385754022216923412",
    "ZIMMERMANN": "5385754022216923412",
    "EXCLUSIVE": "5385754022216923412",
    "Ralph Lauren": "5385754022216923412",
    "BALENCIAGA": "5385754022216923412",
    "FENDI": "5385754022216923412",
    "GUCCI": "5385754022216923412",
    "Сумки Jacquemus": "5385754022216923412",
    "Сумки BALENCIAGA": "5385754022216923412",
    "Кроссовки Louis Vuitton": "5385729374944167175",
    "Кроссовки [LUXURY SNEAKERS]": "5385729374944167175",
    "Сумки DIOR": "5385754022216923412",
    "Сумки GOYARD": "5385754022216923412",
    "Мужские сумки": "5385754022216923412",
    "Чемоданы и дорожные сумки": "5385681076393894670",
    "Сумки BVLGARI": "5385754022216923412",
    "Сумки Manolo Blahnik": "5385754022216923412",
    "Обувь Alaïa": "5385736843026391346",
    "BURBERRY": "5385754022216923412",
    "Moncler": "5385659694513701256",
    "Обвесы на сумку": "5385647869870530128",
    "Кроссовки BALENCIAGA": "5385729374944167175",
    "Обувь Chanel": "5385736843026391346",
    "Обувь для пляжа и бассейна": "5385827020271026144",
    "Женские сапоги": "5385740951102493755",
    "Обувь Loro/Brunello/Kiton/Zegna": "5385729374944167175",
    "Acne Studios": "5385754022216923412",
    "CHROME HEARTS Украшения из серебра": "5385647869870530128",
    "Сумки Chrome Hearts": "5385754022216923412",
    "Товары для дома": "5385763122803256421",
    "Сумки CELINE": "5385754022216923412",
    "Лоферы Loro Piana": "5385729374944167175",
    "Сумки Maison Margiela": "5385754022216923412",
    "Сумки Acne Studios": "5385754022216923412",
    "Сумки LEMAIRE": "5385754022216923412",
    "Украшения (бижутерия)": "5385647869870530128",
    "CANADA GOOSE": "5385659694513701256",
    "Yves Saint Laurent": "5385754022216923412",
    "AMI Paris": "5385754022216923412",
    "Кроссовки LOEWE": "5385729374944167175",
    "Кроссовки GUCCI": "5385729374944167175",
    "Arcteryx": "5385659694513701256",
    "GIVENCHY": "5385754022216923412",
    "Классическая мужская одежда": "5385713080715649102",
    "MAISON MARGIELA": "5385754022216923412",
    "WELLDONE": "5385754022216923412",
    "AMIRI": "5385754022216923412",
    "Женская обувь II": "5385736843026391346",
    "Сумки Roger Vivier": "5385754022216923412",
    "Сумки Dolce Gabbana": "5385754022216923412",
    "Сумки Alaïa": "5385754022216923412",
    "Зимние куртки": "5385659694513701256",
    "Обувь для детей": "5385729374944167175",
    "Классическая мужская обувь из экзотической кожи": "5385729374944167175",
    "Сумки Ralph Lauren": "5385754022216923412",
    "Сумки MCM": "5385754022216923412",
    "Max Mara": "5385754022216923412",
    "Ассортимент": "5385657221623874687",
    "Пальто": "5385659694513701256",
    "alexander wang": "5385754022216923412",
    "ENFANTS RICHES DEPRIMES": "5385754022216923412",
    "Ювелирные украшения": "5385647869870530128",
    "Обувь Louis Vuitton": "5385729374944167175",
    "Сумки MOYNAT PARIS": "5385754022216923412",
}

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

def delete_all_topics():
    """Удаляет все темы, кроме General, через API бота-админа"""
    logger.info("🔄 Получаем список тем для удаления...")
    url = f"https://api.telegram.org/bot{TOKEN}/getForumTopics"
    payload = {"chat_id": CHAT_ID}
    try:
        resp = requests.post(url, data=payload, timeout=15)
        data = resp.json()
        if not data.get("ok"):
            logger.warning(f"Не удалось получить темы: {data.get('description')}")
            return
        topics = data["result"].get("topics", [])
        deleted = 0
        for topic in topics:
            topic_id = topic.get("message_thread_id")
            if topic_id == 1:
                continue  # Пропускаем General
            del_url = f"https://api.telegram.org/bot{TOKEN}/deleteForumTopic"
            del_payload = {"chat_id": CHAT_ID, "message_thread_id": topic_id}
            try:
                del_resp = requests.post(del_url, data=del_payload, timeout=10)
                if del_resp.json().get("ok"):
                    logger.info(f"🗑️ Удалена тема: {topic.get('name')}")
                    deleted += 1
                time.sleep(1)
            except Exception as e:
                logger.error(f"Ошибка удаления: {e}")
        logger.info(f"Удалено тем: {deleted}")
    except Exception as e:
        logger.error(f"Ошибка получения списка тем: {e}")

def create_topic(name):
    icon_id = ICON_MAP.get(name)
    url = f"https://api.telegram.org/bot{TOKEN}/createForumTopic"
    payload = {"chat_id": CHAT_ID, "name": name}
    if icon_id:
        payload["icon_custom_emoji_id"] = icon_id

    try:
        resp = requests.post(url, data=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            return True, None
        error = data.get("description", "")
        if "TOPIC_NAME_OCCUPIED" in error or "already exists" in error:
            return True, "exists"
        return False, error
    except Exception as e:
        return False, str(e)

def main():
    logger.info("🚀 Запуск очистки и пересоздания тем...")
    
    # 1. Сначала удаляем всё
    delete_all_topics()
    time.sleep(3)

    # 2. Создаём заново
    logger.info("🚀 Начинаю создание тем с анимированными иконками...")
    created = 0; skipped = 0; errors = 0
    total = len(TOPICS)

    for idx, name in enumerate(TOPICS, 1):
        success, msg = create_topic(name)
        if success and msg == "exists":
            logger.info(f"➖ [{idx}/{total}] Пропущено: {name}")
            skipped += 1
        elif success:
            logger.info(f"✅ [{idx}/{total}] Создано: {name}")
            created += 1
        else:
            logger.info(f"❌ [{idx}/{total}] Ошибка: {name} — {msg}")
            errors += 1
        time.sleep(3)

    logger.info(f"🏁 ЗАВЕРШЕНО. Создано: {created}, Пропущено: {skipped}, Ошибок: {errors}")

if __name__ == "__main__":
    main()
