import os
import time
import requests
import logging

# === НАСТРОЙКИ ===
TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = "@trifferi_katalog"

# === СЛОВАРЬ ЭМОДЗИ (Unicode) ДЛЯ КАЖДОЙ ТЕМЫ ===
EMOJI_MAP = {
    # Часы, Ремни
    "Часы": "🕐",
    "Ремень Hermes": "👔",
    "Ремни": "👔",
    # Сумки
    "Сумки Hermes": "👜",
    "Сумки CHANEL": "👜",
    "Сумки THE ROW": "👜",
    "Сумки MIU MIU": "👜",
    "Сумки PRADA": "👜",
    "Сумки YSL": "👜",
    "Сумки Loewe": "👜",
    "Сумки Loro Piana": "👜",
    "Сумки BOTTEGA VENETA": "👜",
    "Сумки Louis Vuitton": "👜",
    "Сумки Jacquemus": "👜",
    "Сумки BALENCIAGA": "👜",
    "Сумки DIOR": "👜",
    "Сумки GOYARD": "👜",
    "Мужские сумки": "💼",
    "Сумки BVLGARI": "👜",
    "Сумки Manolo Blahnik": "👜",
    "Сумки Schiaparelli": "👜",
    "Сумки Chrome Hearts": "👜",
    "Сумки CELINE": "👜",
    "Сумки Maison Margiela": "👜",
    "Сумки Acne Studios": "👜",
    "Сумки LEMAIRE": "👜",
    "Сумки Roger Vivier": "👜",
    "Сумки Dolce Gabbana": "👜",
    "Сумки Alaïa": "👜",
    "Сумки Ralph Lauren": "👜",
    "Сумки MCM": "👜",
    "Сумки MOYNAT PARIS": "👜",
    # Обувь, кроссовки
    "Обувь Hermes": "👟",
    "Женская обувь": "👠",
    "Классическая мужская обувь": "👞",
    "Кроссовки Louis Vuitton": "👟",
    "Кроссовки [LUXURY SNEAKERS]": "👟",
    "Кроссовки BALENCIAGA": "👟",
    "Обувь Chanel": "👠",
    "Обувь для пляжа и бассейна": "🩴",
    "Женские сапоги": "🥾",
    "Обувь Loro/Brunello/Kiton/Zegna": "👞",
    "Лоферы Loro Piana": "👞",
    "Обувь Alaïa": "👠",
    "Женская обувь II": "👠",
    "Обувь для детей": "👟",
    "Классическая мужская обувь из экзотической кожи": "👞",
    "Кроссовки LOEWE": "👟",
    "Кроссовки GUCCI": "👟",
    # Одежда
    "Женская одежда": "👗",
    "Одежда для детей": "👶",
    "Женская верхняя одежда (Кожа, кашемир)": "🧥",
    "Одежда Loro/Brunello/Kiton/Zegna": "👔",
    "Мужская верхняя одежда": "🧥",
    "Классическая мужская одежда": "👔",
    "Зимние куртки": "🧥",
    "Пальто": "🧥",
    "CANADA GOOSE": "🧥",
    "Arcteryx": "🧥",
    "Moncler": "🧥",
    "MAISON MARGIELA": "👔",
    "WELLDONE": "👔",
    "AMIRI": "👔",
    "alexander wang": "👔",
    "ENFANTS RICHES DEPRIMES": "👔",
    # Аксессуары, очки, украшения
    "Очки": "👓",
    "Украшения Schiaparelli": "💎",
    "CHROME HEARTS Украшения из серебра": "💎",
    "Украшения (бижутерия)": "💍",
    "Ювелирные украшения": "💎",
    "Шарфы и шапки": "🧣",
    "Обвесы на сумку": "🎀",
    "Товары для дома": "🏠",
    # Бренды без категории
    "Chanel": "🎀",
    "HERMES": "🎀",
    "CHROME HEARTS": "💎",
    "Dolce&Gabbana": "🎀",
    "ZIMMERMANN": "🎀",
    "EXCLUSIVE": "🎀",
    "Ralph Lauren": "🎀",
    "BALENCIAGA": "🎀",
    "FENDI": "🎀",
    "GUCCI": "🎀",
    "BURBERRY": "🎀",
    "Acne Studios": "🎀",
    "Yves Saint Laurent": "🎀",
    "AMI Paris": "🎀",
    "GIVENCHY": "🎀",
    "Max Mara": "🎀",
    # Пляж
    "Купальники и пляжная одежда": "🩱",
    # Прочее
    "Чемоданы и дорожные сумки": "🧳",
    "Ассортимент": "📦"
}

# Полный список тем
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

def create_topic_with_emoji(original_name):
    # Берём эмодзи из словаря или ставим 📦 по умолчанию
    emoji = EMOJI_MAP.get(original_name, "📦")
    # Формируем новое название: "👜 Сумки Hermes"
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
    logger.info("🚀 Начинаю создание тем с эмодзи в названии...")
    created = 0; skipped = 0; errors = 0
    total = len(TOPICS)

    for idx, name in enumerate(TOPICS, 1):
        success, msg = create_topic_with_emoji(name)
        if success and msg == "exists":
            logger.info(f"➖ [{idx}/{total}] Пропущено (уже есть): {name}")
            skipped += 1
        elif success:
            logger.info(f"✅ [{idx}/{total}] Создано: {name}")
            created += 1
        else:
            logger.info(f"❌ [{idx}/{total}] Ошибка: {name} — {msg}")
            errors += 1
        time.sleep(1)

    logger.info(f"🏁 ЗАВЕРШЕНО. Создано: {created}, Пропущено: {skipped}, Ошибок: {errors}")

if __name__ == "__main__":
    main()
