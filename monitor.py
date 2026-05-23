import os
import requests
from bs4 import BeautifulSoup

URL = "https://store.plusmember.jp/shinsekai_produce101/products/detail.php?product_id=107201"

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(URL, headers=headers, timeout=20).text
soup = BeautifulSoup(html, "html.parser")
text = soup.get_text(" ", strip=True)

is_sold_out = "SOLD OUT" in text
is_available = ("カートに入れる" in text) or ("購入" in text and not is_sold_out)

if is_available:
    message = "在庫復活！\nアクリルスタンド KINARI（釼持 吉成）\n" + URL

    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "to": LINE_USER_ID,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        },
        timeout=20
    )

    print("LINE通知送信")
else:
    print("まだSOLD OUT")
