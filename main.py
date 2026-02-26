import requests
import os
import json

# --- КОНФИГУРАЦИЯ ---
PRODUCT_ID = 116659588
DEST_LOCATION = -5854091 # Новосибирск

# Токены из секретов
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def check_stock():
    # Используем URL из вашего лога (внутренний API WB)
    url = "https://www.wildberries.ru/__internal/card/cards/v4/detail"
    
    params = {
        "appType": "1",
        "curr": "rub",
        "dest": DEST_LOCATION,
        "spp": "30",
        "hide_vflags": "4294967296",
        "ab_testing": "false",
        "lang": "ru",
        "nm": PRODUCT_ID
    }
    
    # Минимальные заголовки, чтобы WB принял запрос (взято из вашего лога)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "x-requested-with": "XMLHttpRequest",
        "x-spa-version": "13.24.8" # Важно: версия SPA из вашего лога
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Проверка структуры ответа
        products = data.get("data", {}).get("products", [])
        if not products:
            print("Товар не найден в ответе API.")
            return

        product = products[0]
        name = product.get("name", "Неизвестный товар")
        
        total_quantity = 0
        stock_info = []

        # sizes содержит остатки
        for size in product.get("sizes", []):
            size_name = size.get("name", "Стандарт")
            # Суммируем количество по всем складам для данного размера
            qty = sum(stock.get("qty", 0) for stock in size.get("stocks", []))
            total_quantity += qty
            if qty > 0:
                stock_info.append(f"Вариант '{size_name}': {qty} шт.")

        if total_quantity > 0:
            message = (
                f"🎉 **Торт '{name}' в наличии!**\n\n"
                f"**Общий остаток:** {total_quantity} шт.\n"
                f"**Детали:**\n" + "\n".join(stock_info) + 
                f"\n\n[Ссылка на товар](https://www.wildberries.ru/catalog/{PRODUCT_ID}/detail.aspx)"
            )
            print(f"Найдено наличие: {total_quantity} шт. Отправка уведомления...")
            send_telegram_message(message)
        else:
            print(f"Товар есть в каталоге, но остаток 0 шт.")

    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e}")
        print(f"Текст ответа сервера: {response.text}")
    except Exception as e:
        print(f"Ошибка при выполнении: {e}")

def send_telegram_message(text):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("ОШИБКА: Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID в секретах репозитория!")
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
