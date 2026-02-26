import requests
import os
import json

# --- КОНФИГУРАЦИЯ ---
PRODUCT_ID = 116659588  # ID торта
DEST_LOCATION = -1257786 # Ваш регион (можно менять)

# Токены из секретов
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def check_stock():
    # URL, который вы нашли и проверили
    url = "https://search.wb.ru/exactmatch/ru/common/v4/search"
    
    # Параметры поиска
    params = {
        "appType": 1,
        "curr": "rub",
        "dest": DEST_LOCATION,
        "query": PRODUCT_ID,  # Ищем по ID товара
        "resultset": "catalog",
        "limit": 1            # Нам нужен только один товар
    }
    
    # Минимальные заголовки (как в вашем рабочем примере)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        # Логика обработки ответа поиска
        products = data.get("products", [])
        
        if not products:
            print("Товар не найден в результатах поиска (возможно, снят с продажи).")
            return

        product = products[0]
        name = product.get("name", "Товар")
        
        # В поиске количество лежит в поле 'quantity'
        # Оно показывает, сколько единиц доступно для покупки в вашем регионе
        quantity = product.get("quantity", 0)
        
        # Цена
        price = product.get("salePriceU", 0) / 100 # Цена в копейках, переводим в рубли

        if quantity > 0:
            message = (
                f"🎉 **Торт '{name}' в наличии!**\n\n"
                f"**Доступно:** {quantity} шт.\n"
                f"**Цена:** {price:.0f} руб.\n\n"
                f"[Ссылка на товар](https://www.wildberries.ru/catalog/{PRODUCT_ID}/detail.aspx)"
            )
            print(f"Найдено наличие: {quantity} шт. Отправка уведомления...")
            send_telegram_message(message)
        else:
            print(f"Товар найден, но остаток 0 (quantity={quantity}).")

    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e}")
    except Exception as e:
        print(f"Ошибка при выполнении: {e}")

def send_telegram_message(text):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("ОШИБКА: Не заданы секреты TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID!")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true"
    }
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code != 200:
            print(f"Ошибка Telegram API: {resp.text}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

if __name__ == "__main__":
    check_stock()
