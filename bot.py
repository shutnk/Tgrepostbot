import os
import time
import requests
import logging

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = -1003991874844

# === ЭМОДЗИ ДЛЯ КАЖДОЙ ТЕМЫ (Telegram сам превратит их в иконки) ===
TOPIC_EMOJIS = {
    "Часы": "🕐",
    "Сумки Hermes": "👜",
    "Обувь Hermes": "👟",
    "Ремень Hermes": "🔗",
    "Сумки CHANEL": "👜",
    "Женская одежда": "👗",
    "Сумки THE ROW": "👜",
    "Chanel": "👜",
    "Сумки MIU MIU": "👜",
    "Одежда для детей": "🧸",
    "Сумки PRADA": "👜",
    "CHROME HEARTS": "💎",
    "Женская обувь": "👠",
    "Сумки YSL": "👜",
    "Женская верхняя одежда (Кожа, кашемир)": "🧥",
    "Ремни": "🔗",
    "Шарфы и шапки": "🧣",
    "Одежда Loro/Brunello/Kiton/Zegna": "👔",
    "Очки": "👓",
    "Украшения Schiaparelli": "💍",
    "Сумки Schiaparelli": "👜",
    "Dolce&Gabbana": "👜",
    "Мужская верхняя одежда": "🧥",
    "Купальники и пляжная одежда": "🩱",
    "Сумки Loewe": "👜",
    "Сумки Loro Piana": "👜",
    "Сумки BOTTEGA VENETA": "👜",
    "Классическая мужская обувь": "👞",
    "Сумки Louis Vuitton": "👜",
    "ZIMMERMANN": "👜",
    "EXCLUSIVE": "👜",
    "Ralph Lauren": "👜",
    "BALENCIAGA": "👜",
    "FENDI": "👜",
    "GUCCI": "👜",
    "Сумки Jacquemus": "👜",
    "Сумки BALENCIAGA": "👜",
    "Кроссовки Louis Vuitton": "👟",
    "Кроссовки [LUXURY SNEAKERS]": "👟",
    "Сумки DIOR": "👜",
    "Сумки GOYARD": "👜",
    "Мужские сумки": "💼",
    "Чемоданы и дорожные сумки": "🧳",
    "Сумки BVLGARI": "👜",
    "Сумки Manolo Blahnik": "👜",
    "Обувь Alaïa": "👠",
    "BURBERRY": "👜",
    "Moncler": "🧥",
    "Обвесы на сумку": "🎀",
    "Кроссовки BALENCIAGA": "👟",
    "Обувь Chanel": "👠",
    "Обувь для пляжа и бассейна": "🩴",
    "Женские сапоги": "🥾",
    "Обувь Loro/Brunello/Kiton/Zegna": "👞",
    "Acne Studios": "👜",
    "CHROME HEARTS Украшения из серебра": "💍",
    "Сумки Chrome Hearts": "👜",
    "Товары для дома": "🏠",
    "Сумки CELINE": "👜",
    "Лоферы Loro Piana": "👞",
    "Сумки Maison Margiela": "👜",
    "Сумки Acne Studios": "👜",
    "Сумки LEMAIRE": "👜",
    "Украшения (бижутерия)": "💍",
    "CANADA GOOSE": "🧥",
    "Yves Saint Laurent": "👜",
    "AMI Paris": "👜",
    "Кроссовки LOEWE": "👟",
    "Кроссовки GUCCI": "👟",
    "Arcteryx": "🧥",
    "GIVENCHY": "👜",
    "Классическая мужская одежда": "👔",
    "MAISON MARGIELA": "👜",
    "WELLDONE": "👜",
    "AMIRI": "👜",
    "Женская обувь II": "👠",
    "Сумки Roger Vivier": "👜",
    "Сумки Dolce Gabbana": "👜",
    "Сумки Alaïa": "👜",
    "Зимние куртки": "🧥",
    "Обувь для детей": "👟",
    "Классическая мужская обувь из экзотической кожи": "👞",
    "Сумки Ralph Lauren": "👜",
    "Сумки MCM": "👜",
    "Max Mara": "👜",
    "Ассортимент": "📦",
    "Пальто": "🧥",
    "alexander wang": "👜",
    "ENFANTS RICHES DEPRIMES": "👜",
    "Ювелирные украшения": "💍",
    "Обувь Louis Vuitton": "👟",
    "Сумки MOYNAT PARIS": "👜"
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

def create_topic(original_name):
    emoji = TOPIC_EMOJIS.get(original_name, "🔹")
    full_name = f"{emoji} {original_name}"

    url = f"https://api.telegram.org/bot{TOKEN}/createForumTopic"
    payload = {
        "chat_id": CHAT_ID,
        "name": full_name
    }
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
    logger.info(f"🚀 Запуск создания тем в группе {CHAT_ID}...")
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
        time.sleep(5)

    logger.info(f"🏁 ЗАВЕРШЕНО. Создано: {created}, Пропущено: {skipped}, Ошибок: {errors}")

if __name__ == "__main__":
    main()
