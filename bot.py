import os
import time
import requests
import logging

# === НАСТРОЙКИ ===
TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = "@trifferi_katalog"

# === СЛОВАРЬ ТЕМ И ИХ ID ЭМОДЗИ (из Telegram) ===
# ID взяты из официального набора Telegram Custom Emoji
EMOJI_MAP = {
    # Часы, Ремни
    "Часы": "5300964753318576962",  # 🕐
    "Ремень Hermes": "5300973215809732663",  # 👔
    "Ремни": "5300973215809732663",
    # Сумки (иконка сумки)
    "Сумки Hermes": "5300959207336386686",  # 👜
    "Сумки CHANEL": "5300959207336386686",
    "Сумки THE ROW": "5300959207336386686",
    "Сумки MIU MIU": "5300959207336386686",
    "Сумки PRADA": "5300959207336386686",
    "Сумки YSL": "5300959207336386686",
    "Сумки Loewe": "5300959207336386686",
    "Сумки Loro Piana": "5300959207336386686",
    "Сумки BOTTEGA VENETA": "5300959207336386686",
    "Сумки Louis Vuitton": "5300959207336386686",
    "Сумки Jacquemus": "5300959207336386686",
    "Сумки BALENCIAGA": "5300959207336386686",
    "Сумки DIOR": "5300959207336386686",
    "Сумки GOYARD": "5300959207336386686",
    "Мужские сумки": "5300959207336386686",
    "Сумки BVLGARI": "5300959207336386686",
    "Сумки Manolo Blahnik": "5300959207336386686",
    "Сумки Schiaparelli": "5300959207336386686",
    "Сумки Chrome Hearts": "5300959207336386686",
    "Сумки CELINE": "5300959207336386686",
    "Сумки Maison Margiela": "5300959207336386686",
    "Сумки Acne Studios": "5300959207336386686",
    "Сумки LEMAIRE": "5300959207336386686",
    "Сумки Roger Vivier": "5300959207336386686",
    "Сумки Dolce Gabbana": "5300959207336386686",
    "Сумки Alaïa": "5300959207336386686",
    "Сумки Ralph Lauren": "5300959207336386686",
    "Сумки MCM": "5300959207336386686",
    "Сумки MOYNAT PARIS": "5300959207336386686",
    # Обувь (кроссовки, туфли)
    "Обувь Hermes": "5300964600011554392",  # 👟
    "Женская обувь": "5300970331105097933",  # 👠
    "Классическая мужская обувь": "5300964600011554392",
    "Кроссовки Louis Vuitton": "5300964600011554392",
    "Кроссовки [LUXURY SNEAKERS]": "5300964600011554392",
    "Кроссовки BALENCIAGA": "5300964600011554392",
    "Обувь Chanel": "5300970331105097933",
    "Обувь для пляжа и бассейна": "5300970331105097933",
    "Женские сапоги": "5300966823945895409",  # 🥾
    "Обувь Loro/Brunello/Kiton/Zegna": "5300964600011554392",
    "Лоферы Loro Piana": "5300964600011554392",
    "Обувь Alaïa": "5300970331105097933",
    "Женская обувь II": "5300970331105097933",
    "Обувь для детей": "5300964600011554392",
    "Классическая мужская обувь из экзотической кожи": "5300964600011554392",
    "Кроссовки LOEWE": "5300964600011554392",
    "Кроссовки GUCCI": "5300964600011554392",
    # Одежда (футболки, платья, пальто)
    "Женская одежда": "5300968087145451169",  # 👗
    "Одежда для детей": "5300969600105356396",  # 👶
    "Женская верхняя одежда (Кожа, кашемир)": "5300968087145451169",
    "Одежда Loro/Brunello/Kiton/Zegna": "5300968087145451169",
    "Мужская верхняя одежда": "5300973215809732663",  # 👔
    "Классическая мужская одежда": "5300973215809732663",
    "Зимние куртки": "5300961868741878404",  # 🧥
    "Пальто": "5300961868741878404",
    "CANADA GOOSE": "5300961868741878404",
    "Arcteryx": "5300961868741878404",
    "Moncler": "5300961868741878404",
    "MAISON MARGIELA": "5300968087145451169",
    "WELLDONE": "5300968087145451169",
    "AMIRI": "5300968087145451169",
    "alexander wang": "5300968087145451169",
    "ENFANTS RICHES DEPRIMES": "5300968087145451169",
    # Аксессуары, очки, украшения
    "Очки": "5300950591712166544",  # 👓
    "Украшения Schiaparelli": "5300958891576933556",  # 💎
    "CHROME HEARTS Украшения из серебра": "5300958891576933556",
    "Украшения (бижутерия)": "5300958891576933556",
    "Ювелирные украшения": "5300958891576933556",
    "Шарфы и шапки": "5300964665757724836",  # 🧣
    "Обвесы на сумку": "5300950591712166544",
    "Товары для дома": "5300963679853667328",  # 🏠
    # Бренды без конкретной категории (ставим модную иконку)
    "Chanel": "5300963535739823924",  # 🎀
    "HERMES": "5300963535739823924",
    "CHROME HEARTS": "5300958891576933556",
    "Dolce&Gabbana": "5300963535739823924",
    "ZIMMERMANN": "5300963535739823924",
    "EXCLUSIVE": "5300963535739823924",
    "Ralph Lauren": "5300963535739823924",
    "BALENCIAGA": "5300963535739823924",
    "FENDI": "5300963535739823924",
    "GUCCI": "5300963535739823924",
    "BURBERRY": "5300963535739823924",
    "Acne Studios": "5300963535739823924",
    "Yves Saint Laurent": "5300963535739823924",
    "AMI Paris": "5300963535739823924",
    "GIVENCHY": "5300963535739823924",
    "Max Mara": "5300963535739823924",
    # Пляж, бассейн, купальники
    "Купальники и пляжная одежда": "5300969061681453152",  # 🩱
    "Сумки": "5300959207336386686",
    # Остальное
    "Чемоданы и дорожные сумки": "5300959207336386686",
    "Ассортимент": "5300961089721270393",  # 📦
}

# Полный список тем (оставил твой оригинальный список без изменений)
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
    # Если для темы нет иконки, ставим стандартную синюю (эмодзи с цифрой)
    emoji_id = EMOJI_MAP.get(name, "5300961089721270393")  # 📦 как запасной вариант

    url = f"https://api.telegram.org/bot{TOKEN}/createForumTopic"
    payload = {
        "chat_id": CHAT_ID,
        "name": name,
        "icon_custom_emoji_id": emoji_id
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
    logger.info("🚀 Начинаю создание тем с иконками (эмодзи)...")
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
        time.sleep(1)  # Пауза чтобы не спамить API

    logger.info(f"🏁 ЗАВЕРШЕНО. Создано: {created}, Пропущено: {skipped}, Ошибок: {errors}")

if __name__ == "__main__":
    main()
