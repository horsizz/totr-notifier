import requests

NM_ID = 116659588  # id товара

url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={NM_ID}"

response = requests.get(url)
data = response.json()

product = data["data"]["products"][0]

in_stock = product["totalQuantity"] > 0

print("В наличии:", in_stock)
