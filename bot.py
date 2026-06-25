import os
import time
import requests
import logging

# === НАСТРОЙКИ ===
TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = "@trifferi_katalog"

# === ОФИЦИАЛЬНЫЕ ID АНИМИРОВАННЫХ ИКОНОК TELEGRAM (Свежие, рабочие) ===
ICON_MAP = {
    "Часы": "5385654382486539496",       # Часы (анимированные)
    "Сумки Hermes": "5385754022216923412",  # Сумка (коричневая)
    "Сумки CHANEL": "5385754022216923412",
    "Сумки THE ROW": "5385754022216923412",
    "Сумки MIU MIU": "5385754022216923412",
    "Сумки PRADA": "5385754022216923412",
    "Сумки YSL": "5385754022216923412",
    "Сумки Loewe": "5385754022216923412",
    "Сумки Loro Piana": "5385754022216923412",
    "Сумки BOTTEGA VENETA": "5385754022216923412",
    "Сумки Louis Vuitton": "5385754022216923412",
    "Сумки Jacquemus": "5385754022216923412",
    "Сумки BALENCIAGA": "5385754022216923412",
    "Сумки DIOR": "5385754022216923412",
    "Сумки GOYARD": "5385754022216923412",
    "Мужские сумки": "5385754022216923412",
    "Сумки BVLGARI": "5385754022216923412",
    "Сумки Manolo Blahnik": "5385754022216923412",
    "Сумки Schiaparelli": "5385754022216923412",
    "Сумки Chrome Hearts": "5385754022216923412",
    "Сумки CELINE": "5385754022216923412",
    "Сумки Maison Margiela": "5385754022216923412",
    "Сумки Acne Studios": "5385754022216923412",
    "Сумки LEMAIRE": "5385754022216923412",
    "Сумки Roger Vivier": "5385754022216923412",
    "Сумки Dolce Gabbana": "5385754022216923412",
    "Сумки Alaïa": "5385754022216923412",
    "Сумки Ralph Lauren": "5385754022216923412",
    "Сумки MCM": "5385754022216923412",
    "Сумки MOYNAT PARIS": "5385754022216923412",
    # Обувь
    "Обувь Hermes": "5385729374944167175", # Кроссовок
    "Женская обувь": "5385736843026391346", # Красная туфелька
    "Классическая мужская обувь": "5385729374944167175",
    "Кроссовки Louis Vuitton": "5385729374944167175",
    "Кроссовки [LUXURY SNEAKERS]": "5385729374944167175",
    "Кроссовки BALENCIAGA": "5385729374944167175",
    "Обувь Chanel": "5385736843026391346",
    "Обувь для пляжа и бассейна": "5385827020271026144", # Шлёпанец
    "Женские сапоги": "5385740951102493755", # Зелёный сапог
    "Обувь Loro/Brunello/Kiton/Zegna": "5385729374944167175",
    "Лоферы Loro Piana": "5385729374944167175",
    "Обувь Alaïa": "5385736843026391346",
    "Женская обувь II": "5385736843026391346",
    "Обувь для детей": "5385729374944167175",
    "Классическая мужская обувь из экзотической кожи": "5385729374944167175",
    "Кроссовки LOEWE": "5385729374944167175",
    "Кроссовки GUCCI": "5385729374944167175",
    # Одежда
    "Женская одежда": "5385707592904087822", # Жёлтое платье
    "Одежда для детей": "5385783281911921219", # Ребёнок
    "Женская верхняя одежда (Кожа, кашемир)": "5385707592904087822",
    "Одежда Loro/Brunello/Kiton/Zegna": "5385713080715649102", # Рубашка
    "Мужская верхняя одежда": "5385713080715649102",
    "Классическая мужская одежда": "5385713080715649102",
    "Зимние куртки": "5385659694513701256", # Зимняя куртка
    "Пальто": "5385659694513701256",
    "CANADA GOOSE": "5385659694513701256",
    "Arcteryx": "5385659694513701256",
    "Moncler": "5385659694513701256",
    "MAISON MARGIELA": "5385713080715649102",
    "WELLDONE": "5385713080715649102",
    "AMIRI": "5385713080715649102",
    "alexander wang": "5385713080715649102",
    "ENFANTS RICHES DEPRIMES": "5385713080715649102",
    # Аксессуары, очки, украшения
    "Очки": "5385685000368160908", # Очки
    "Украшения Schiaparelli": "5385647869870530128", # Бриллиант
    "CHROME HEARTS Украшения из серебра": "5385647869870530128",
    "Украшения (бижутерия)": "5385647869870530128",
    "Ювелирные украшения": "5385647869870530128",
    "Шарфы и шапки": "5385759624885116002", # Шарф
    "Обвесы на сумку": "5385647869870530128",
    "Товары для дома": "5385763122803256421", # Домик
    # Бренды без категрии
    "Chanel": "5385754022216923412",
    "CHROME HEARTS": "5385647869870530128",
    "Dolce&Gabbana": "5385754022216923412",
    "ZIMMERMANN": "5385754022216923412",
    "EXCLUSIVE": "5385754022216923412",
    "Ralph Lauren": "5385754022216923412",
    "BALENCIAGA": "5385754022216923412",
    "FENDI": "5385754022216923412",
    "GUCCI": "5385754022216923412",
    "BURBERRY": "5385754022216923412",
    "Acne Studios": "5385754022216923412",
    "Yves Saint Laurent": "5385754022216923412",
    "AMI Paris": "5385754022216923412",
    "GIVENCHY": "5385754022216923412",
    "Max Mara": "5385754022216923412",
    # Остальное
    "Ремень Hermes": "5385785779086361281", # Красный ремень
    "Ремни": "5385785779086361281",
    "Купальники и пляжная одежда": "5385819370870144587", # Купальник
    "Чемоданы и дорожные сумки": "5385681076393894670", # Чемодан
    "Ассортимент": "5385657221623874687", # Коробка
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

def create_topic_with_icon(name):
    icon_id = ICON_MAP.get(name, None)  # Если иконки нет в базе, Telegram поставит букву

    url = f"https://api.telegram.org/bot{TOKEN}/createForumTopic"
    payload = {
        "chat_id": CHAT_ID,
        "name": name
    }
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
    logger.info("🚀 Начинаю создание тем с ПРАВИЛЬНЫМИ анимированными иконками...")
    created = 0; skipped = 0; errors = 0
    total = len(TOPICS)

    for idx, name in enumerate(TOPICS, 1):
        success, msg = create_topic_with_icon(name)
        if success and msg == "exists":
            logger.info(f"➖ [{idx}/{total}] Пропущено (уже есть): {name}")
            skipped += 1
        elif success:
            logger.info(f"✅ [{idx}/{total}] Создано с иконкой: {name}")
            created += 1
        else:
            logger.info(f"❌ [{idx}/{total}] Ошибка: {name} — {msg}")
            errors += 1
        # Ждём 5 секунд, чтобы точно не было Too Many Requests
        time.sleep(5)

    logger.info(f"🏁 ЗАВЕРШЕНО. Создано: {created}, Пропущено: {skipped}, Ошибок: {errors}")

if __name__ == "__main__":
    main()
