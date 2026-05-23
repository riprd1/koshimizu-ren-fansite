import os
import json
import requests
from bs4 import BeautifulSoup

PRODUCT_URL = "https://store.plusmember.jp/shinsekai_produce101/products/detail.php?product_id=107201"
STATE_FILE = "state.json"
LINE_PUSH_API = "https://api.line.me/v2/bot/message/push"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(PRODUCT_URL, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    is_sold_out = "SOLD OUT" in text
    has_cart = "カートに入れる" in text or "購入手続き" in text

    if is_sold_out:
        status = "sold_out"
    elif has_cart:
        status = "available"
    else:
        status = "unknown"

    return {
        "status": status,
        "is_sold_out": is_sold_out,
        "has_cart": has_cart
    }

def send_line_message(text):
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    r = requests.post(LINE_PUSH_API, headers=headers, json=payload, timeout=20)
    r.raise_for_status()

def main():
    state = load_state()
    result = check_stock()

    current_status = result["status"]
    last_status = state.get("last_status")

    print("Current status:", current_status)
    print("Last status:", last_status)

    # 初回実行時は状態だけ保存して通知しない
    if last_status is None:
        state["last_status"] = current_status
        save_state(state)
        print("Initial state saved")
        return

    # SOLD OUT から在庫ありに変わった時だけ通知
    if last_status == "sold_out" and current_status == "available":
        message = (
            "🔔 在庫復活の可能性あり！\n\n"
            "アクリルスタンド KINARI（釼持 吉成）\n\n"
            f"{PRODUCT_URL}"
        )
        send_line_message(message)
        print("Stock restored and notified")

    state["last_status"] = current_status
    save_state(state)

if __name__ == "__main__":
    main()
