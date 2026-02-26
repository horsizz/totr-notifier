import requests
import os

# --- КОНФИГУРАЦИЯ ---
PRODUCT_ID = 116659588  # ID торта Чародейка
DEST_LOCATION = -5854091 # Ваш регион (определен из вашего лога)

# Токен и Chat ID берем из секретов GitHub
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def check_stock():
    # API Wildberries для получения информации о карточке товара
    # Используем стандартный endpoint, который отдает остатки
    url = f"https://card.wb.ru/cards/detail"
    
    params = {
        "appType": 1,
        "curr": "rub",
        "dest": DEST_LOCATION, 
        "spp": 30,
        "ab_testing": "false",
        "lang": "ru",
        "nm": PRODUCT_ID
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Парсинг ответа
        products = data.get("data", {}).get("products", [])
        if not products:
            print("Товар не найден или снят с продажи.")
            return

        product = products[0]
        name = product.get("name", "Неизвестный товар")
        
        total_quantity = 0
        stock_info = []

        # sizes содержит информацию о вариантах (размер/вес) и остатках
        for size in product.get("sizes", []):
            size_name = size.get("name", "Стандарт")
            qty = sum(stock.get("qty", 0) for stock in size.get("stocks", []))
            total_quantity += qty
            if qty > 0:
                stock_info.append(f"Вариант '{size_name}': {qty} шт.")

        if total_quantity > 0:
            message = (
                f"🛒 **Торт Чародейка в наличии!**\n\n"
                f"**Остаток:** {total_quantity} шт.\n"
                f"**Детали:**\n" + "\n".join(stock_info) + 
                f"\n\n[Ссылка на товар](https://www.wildberries.ru/catalog/{PRODUCT_ID}/detail.aspx)"
            )
            send_telegram_message(message)
            print(f"Наличие найдено: {total_quantity} шт. Уведомление отправлено.")
        else:
            print("Товар закончился во всех вариантах.")

    except Exception as e:
        print(f"Ошибка при проверке: {e}")

def send_telegram_message(text):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("Не заданы переменные окружения для Telegram.")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

if __name__ == "__main__":
    check_stock()
