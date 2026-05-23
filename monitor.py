import os
import requests
from bs4 import BeautifulSoup

URL = "https://store.plusmember.jp/shinsekai_produce101/products/detail.php?product_id=107201"
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(URL, headers=headers, timeout=20).text
soup = BeautifulSoup(html, "html.parser")
text = soup.get_text(" ", strip=True)

is_sold_out = "SOLD OUT" in text
is_available = ("カートに入れる" in text) or ("購入" in text and not is_sold_out)

if is_available:
    message = f"在庫復活の可能性あり！\nアクリルスタンド KINARI（釼持 吉成）\n{URL}"
    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": message}, timeout=20)
    print(message)
else:
    print("まだSOLD OUTです")
