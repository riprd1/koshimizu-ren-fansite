import os
import requests

LINE_PUSH_API = "https://api.line.me/v2/bot/message/push"

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

    r = requests.post(
        LINE_PUSH_API,
        headers=headers,
        json=payload,
        timeout=20
    )

    print(r.status_code)
    print(r.text)

    r.raise_for_status()

def main():
    send_line_message("✅ GitHub Actions テスト通知")

if __name__ == "__main__":
    main()
