import os
import logging
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8927033296:AAFbS1PZ5UjAoot5uaa5IfwWkCfYh2FYgA4"
CHAT_ID = "@trifferi_katalog"

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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def create_topics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🚀 Начинаю создание {len(TOPICS)} тем в {CHAT_ID}...")
    bot = context.bot
    created = 0; skipped = 0; errors = 0
    for idx, topic_name in enumerate(TOPICS, 1):
        try:
            await bot.create_forum_topic(chat_id=CHAT_ID, name=topic_name)
            created += 1
            await update.message.reply_text(f"✅ [{idx}/{len(TOPICS)}] Создано: {topic_name}")
        except Exception as e:
            if "TOPIC_NAME_OCCUPIED" in str(e) or "already exists" in str(e):
                skipped += 1
                await update.message.reply_text(f"➖ [{idx}/{len(TOPICS)}] Пропущено (уже есть): {topic_name}")
            else:
                errors += 1
                await update.message.reply_text(f"❌ [{idx}/{len(TOPICS)}] Ошибка '{topic_name}': {e}")
    await update.message.reply_text(f"🏁 ЗАВЕРШЕНО. Создано: {created}, Пропущено: {skipped}, Ошибок: {errors}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен!\nИспользуй: /createtopics")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("createtopics", create_topics_command))
    print("[SWILL] Бот запущен на Render. Ожидание команд...")
    app.run_polling()

if __name__ == "__main__":
    main()
