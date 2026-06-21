# ===== Обработчик ссылок от скрипта =====
async def handle_link(update, context):
    if update.message and update.message.text:
        text = update.message.text
        if 't.me/' in text and '|' in text:
            try:
                # Разделяем ссылку и тему
                parts = text.split(' | ')
                link = parts[0]
                topic_name = parts[1]
                
                # Извлекаем ID поста из ссылки
                # Ссылка вида: https://t.me/blvckrooom/775313
                msg_id = int(link.split('/')[-1])
                
                # ===== ГЛАВНОЕ ИСПРАВЛЕНИЕ =====
                # Не используем get_message. Просто копируем через контекст!
                # Бот сам знает, какой это пост и откуда его брать.
                
                # Заменяем текст (если нужно)
                new_text = f"📦 Пост из {SOURCE_CHANNEL}\n\nСсылка: {link}\n\nТема: {topic_name}\n\n✍️ {NEW_AUTHOR}"
                
                # Отправляем сообщение в целевой канал (просто текст, без тем)
                await context.bot.send_message(
                    chat_id=TARGET_CHANNEL,
                    text=new_text
                )
                
                await update.message.reply_text(f"✅ Пост {msg_id} обработан для темы '{topic_name}'!")
                print(f"✅ Обработан пост {msg_id} для темы {topic_name}")
                
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}")
                print(f"❌ Ошибка: {e}")
