import asyncio
import base64
import os
from telethon import TelegramClient

API_ID = 17349
API_HASH = '344583e45741c457fe1862106095a5eb'

TOPICS = [
    "HERMES", "Сумки Hermes", "Обувь Hermes", "Ремень Hermes",
    "Chanel", "Сумки CHANEL", "Обувь Chanel",
    "DIOR", "Сумки DIOR",
    "Louis Vuitton", "Сумки Louis Vuitton", "Обувь Louis Vuitton",
    "PRADA", "Сумки PRADA",
    "GUCCI", "Кроссовки GUCCI",
    "BALENCIAGA", "Сумки BALENCIAGA", "Кроссовки BALENCIAGA",
    "FENDI", "Сумки FENDI",
    "Loewe", "Сумки Loewe", "Кроссовки LOEWE",
    "BOTTEGA VENETA", "Сумки BOTTEGA VENETA",
    "CELINE", "Сумки CELINE",
    "GIVENCHY",
    "Yves Saint Laurent", "Сумки YSL",
    "MIU MIU", "Сумки MIU MIU",
    "THE ROW", "Сумки THE ROW",
    "Ralph Lauren", "Сумки Ralph Lauren",
    "MCM", "Сумки MCM",
    "MOYNAT PARIS", "Сумки MOYNAT PARIS",
    "Acne Studios", "Сумки Acne Studios",
    "LEMAIRE", "Сумки LEMAIRE",
    "Maison Margiela", "Сумки Maison Margiela",
    "Chrome Hearts", "Сумки Chrome Hearts", "CHROME HEARTS Украшения из серебра",
    "Jacquemus", "Сумки Jacquemus",
    "BVLGARI", "Сумки BVLGARI",
    "Manolo Blahnik", "Сумки Manolo Blahnik",
    "Roger Vivier", "Сумки Roger Vivier",
    "Dolce Gabbana", "Сумки Dolce Gabbana",
    "Alaïa", "Сумки Alaïa", "Обувь Alaïa",
    "Schiaparelli", "Сумки Schiaparelli", "Украшения Schiaparelli",
    "Arcteryx",
    "Moncler",
    "CANADA GOOSE",
    "BURBERRY",
    "Max Mara",
    "ZIMMERMANN",
    "AMI Paris",
    "WELLDONE",
    "alexander wang",
    "ENFANTS RICHES DEPRIMES",
    "EXCLUSIVE",
    "Классическая мужская одежда",
    "Классическая мужская обувь",
    "Классическая мужская обувь из экзотической кожи",
    "Женская обувь",
    "Женские сапоги",
    "Женская обувь II",
    "Обувь Loro/Brunello/Kiton/Zegna",
    "Одежда Loro/Brunello/Kiton/Zegna",
    "Лоферы Loro Piana",
    "Обувь для пляжа и бассейна",
    "Обувь для детей",
    "Кроссовки [LUXURY SNEAKERS]",
    "Кроссовки Louis Vuitton",
    "Кроссовки LOEWE",
    "Зимние куртки",
    "Пальто",
    "Женская верхняя одежда(Кожа,кашемир)",
    "Мужская верхняя одежда",
    "Женская одежда",
    "Одежда для детей",
    "Купальники и пляжная одежда",
    "Ремни",
    "Очки",
    "Часы",
    "Ювелирные украшения",
    "Украшения(бижутерия)",
    "Шарфы и шапки",
    "Товары для дома",
    "Обвесы на сумку",
    "Чемоданы и дорожные сумки",
    "Мужские Сумки",
    "Сумки GOYARD",
    "Ассортимент"
]

async def main():
    client = TelegramClient('temp_session', API_ID, API_HASH)
    await client.start(phone='+79030406091')
    print("✅ Сессия создана!")
    
    group = await client.get_entity(-1003991874844)
    print("✅ Группа получена!")
    
    created = 0
    for topic in TOPICS:
        try:
            # Единственный рабочий способ в 1.44.0: отправляем сообщение с reply_to=0
            await client.send_message(
                entity=group,
                message=f"📌 **{topic}**\n\n(Создание темы)",
                reply_to=0
            )
            print(f"✅ Создана тема: {topic}")
            created += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"❌ Ошибка создания '{topic}': {e}")
    
    print(f"🎉 Создано {created} тем!")
    
    # Сохраняем сессию
    with open('session.session', 'rb') as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')
    with open('session.b64', 'w') as f:
        f.write(b64_data)
    print("✅ Файл session.b64 сохранён!")
    
    await client.disconnect()

asyncio.run(main())
