import os
import time
import logging
import base64
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Настройки
SOURCE_CHANNEL = "blvckrooom"  # Без @
DEST_CHANNEL = "trifferi02"    # Без @

def load_session():
    # Загружаем сессию для браузера (если нужно, но selenium работает через cookies)
    # В этом варианте мы будем логиниться вручную один раз через браузер, 
    # а потом сохранять куки.
    pass

def start_browser():
    options = Options()
    options.add_argument("--headless")  # Работает без окна
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    return driver

def login_and_copy(driver):
    logger.info("🚀 Запуск Selenium-бота...")
    
    try:
        # 1. Открываем Web Telegram
        driver.get("https://web.telegram.org/k/")
        time.sleep(10)
        
        # 2. Вводим номер телефона
        phone_input = driver.find_element(By.CSS_SELECTOR, 'input[type="tel"]')
        phone_input.send_keys("+79030406091")
        phone_input.send_keys(Keys.RETURN)
        time.sleep(10)
        
        # 3. Ждём ввода кода (вручную)
        logger.info("⚠️ В Telegram придёт код. Введи его в браузере вручную!")
        input("Нажми Enter в Termux после того, как введёшь код в браузере...")
        time.sleep(5)
        
        # 4. Открываем исходный канал
        driver.get(f"https://web.telegram.org/k/#@{SOURCE_CHANNEL}")
        time.sleep(10)
        
        # 5. Находим посты и копируем
        logger.info(f"📥 Начинаю копирование из {SOURCE_CHANNEL} в {DEST_CHANNEL}...")
        
        # Прокручиваем вниз, чтобы загрузить посты
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(2)
        
        # Находим все сообщения
        posts = driver.find_elements(By.CSS_SELECTOR, '.tgme_widget_message')
        logger.info(f"📄 Найдено постов: {len(posts)}")
        
        for post in posts:
            try:
                # Кликаем на пост (открываем для копирования)
                post.click()
                time.sleep(2)
                
                # Находим кнопку "Переслать"
                forward_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Переслать"]')
                forward_btn.click()
                time.sleep(3)
                
                # Выбираем целевой чат
                chat_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Поиск"]')
                chat_input.send_keys(DEST_CHANNEL)
                time.sleep(2)
                
                # Кликаем на найденный чат
                chat_result = driver.find_element(By.CSS_SELECTOR, '.chatlist-item')
                chat_result.click()
                time.sleep(2)
                
                # Нажимаем "Переслать"
                send_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Переслать"]')
                send_btn.click()
                time.sleep(3)
                
                logger.info("✅ Пост переслан!")
                
            except Exception as e:
                logger.error(f"❌ Ошибка копирования поста: {e}")
                continue
        
        logger.info("🎉 Готово! Все посты скопированы.")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/health")
def health():
    driver = start_browser()
    login_and_copy(driver)
    driver.quit()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
