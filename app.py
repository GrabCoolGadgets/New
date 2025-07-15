import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"

def compress_post(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    compressed = ""
    for i, line in enumerate(lines):
        if line.endswith("{"):
            compressed += line.replace("{", "") + "{"
        elif line == "}":
            compressed += "}"
        else:
            compressed += line + " "
    return compressed.strip()

def update_github_file(new_entry):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("❌ GitHub fetch error:", res.text)
        return False, "❌ GitHub file fetch failed"

    content_data = res.json()
    sha = content_data['sha']
    existing = requests.get(content_data['download_url']).text.strip()

    if new_entry in existing:
        return True, "✅ Duplicate post skipped (already exists)"

    updated = (existing + "\n" + new_entry).strip()

    # Encode content in Base64
    import base64
    encoded = base64.b64encode(updated.encode()).decode()

    payload = {
        "message": "Auto Update from Telegram",
        "content": encoded,
        "sha": sha
    }

    res = requests.put(url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        return True, "✅ Successfully uploaded!"
    else:
        print("❌ Upload failed:", res.text)
        return False, "❌ Failed to upload. Please try again later."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" not in data:
        return "No message", 200

    chat_id = data["message"]["chat"]["id"]

    if "text" not in data["message"]:
        return "No text", 200

    text = data["message"]["text"]

    # Welcome message
    if text == "/start":
        send_message(chat_id, "👋 Welcome! Send me a movie post in the correct format.")
        return "Started", 200

    # Notify uploading
    send_message(chat_id, "📤 Uploading...")

    compressed = compress_post(text)
    success, msg = update_github_file(compressed)

    send_message(chat_id, msg)
    return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
