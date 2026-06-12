import os
import json
import re
import requests
from bs4 import BeautifulSoup

STATE_FILE = "state.json"
LINE_PUSH_API = "https://api.line.me/v2/bot/message/push"

NORMAL_PRODUCTS = [
    {
        "name": "【事後販売】ぷくぷくシール",
        "url": "https://store.plusmember.jp/shinsekai_produce101/products/detail.php?product_id=109573"
    },
    {
        "name": "【事後販売】フォトカード <Final ver.> [11枚セット ランダム/66種]",
        "url": "https://store.plusmember.jp/shinsekai_produce101/products/detail.php?product_id=109570"
    }
]

ACRYLIC_PRODUCT = {
    "name": "【事後販売】アクリルスタンド Final ver.",
    "url": "https://store.plusmember.jp/shinsekai_produce101/products/detail.php?product_id=109572"
}

WATCH_MEMBERS = {
    "TOWA": "TOWA（濱田永遠）",
    "ISSA": "ISSA（柳谷伊冴）",
    "SIYOUNG": "SIYOUNG（パク・シヨン）"
}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def fetch_page(url):
    r = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    return soup, text

def send_line_message(text):
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]

    r = requests.post(
        LINE_PUSH_API,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "to": user_id,
            "messages": [{"type": "text", "text": text}]
        },
        timeout=20
    )
    r.raise_for_status()

def check_normal_product(product):
    soup, text = fetch_page(product["url"])

    is_sold_out = "SOLD OUT" in text
    has_cart = "カートに入れる" in text or "購入手続き" in text

    if is_sold_out:
        return "sold_out"
    if has_cart:
        return "available"
    return "unknown"

def get_sold_out_members_for_acrylic():
    soup, text = fetch_page(ACRYLIC_PRODUCT["url"])

    match = re.search(
        r"以下のメンバーは品切れ中です。(.*?)(ご登録のPlusmember|ログイン|SHARE|$)",
        text
    )

    sold_out_text = match.group(1) if match else ""

    sold_out_members = []

    for code in WATCH_MEMBERS.keys():
        if code in sold_out_text:
            sold_out_members.append(code)

    return sold_out_members

def main():
    state = load_state()

    # 通常商品チェック
    for product in NORMAL_PRODUCTS:
        key = "product:" + product["url"]
        current_status = check_normal_product(product)
        last_status = state.get(key)

        print(product["name"], "current:", current_status, "last:", last_status)

        if last_status == "sold_out" and current_status == "available":
            message = (
                "🔔 在庫復活！\n\n"
                f"{product['name']}\n\n"
                f"{product['url']}"
            )
            send_line_message(message)
            print("Notification sent:", product["name"])

        state[key] = current_status

    # アクリルスタンドの指定メンバーだけチェック
    current_sold_out_members = get_sold_out_members_for_acrylic()

    for code, display_name in WATCH_MEMBERS.items():
        key = "acrylic:" + code
        current_status = "sold_out" if code in current_sold_out_members else "available"
        last_status = state.get(key)

        print(display_name, "current:", current_status, "last:", last_status)

        if last_status == "sold_out" and current_status == "available":
            message = (
                "🔔 アクリルスタンド在庫復活！\n\n"
                f"{display_name}\n\n"
                f"{ACRYLIC_PRODUCT['url']}"
            )
            send_line_message(message)
            print("Notification sent:", display_name)

        state[key] = current_status

    save_state(state)

if __name__ == "__main__":
    main()
