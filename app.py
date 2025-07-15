import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"

# Format text
def compress_post(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    compressed = ""
    for i, line in enumerate(lines):
        if line.endswith("{"):
            compressed += lines[i].replace("{", "") + "{"
        elif line == "}":
            compressed += "}"
        else:
            compressed += line + " "
    return compressed.strip()

# GitHub Update
def update_github_file(new_entry):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("❌ GitHub file fetch failed:", res.status_code, res.text)
        return False

    content_data = res.json()
    sha = content_data['sha']
    existing = requests.get(content_data['download_url']).text.strip()

    if new_entry in existing:
        print("⚠️ Duplicate post skipped.")
        return True

    updated = (existing + "\n" + new_entry).strip()

    from base64 import b64encode
    encoded = b64encode(updated.encode('utf-8')).decode('utf-8')

    payload = {
        "message": "Auto Update from Telegram Bot",
        "content": encoded,
        "sha": sha
    }

    res = requests.put(url, headers=headers, json=payload)
    print("=== GitHub PUT Response ===", res.status_code, res.text)
    return res.status_code in [200, 201]

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    chat_id = data['message']['chat']['id']

    if "text" in data['message']:
        text = data['message']['text']

        if text == "/start":
            send_message(chat_id, "🤖 Welcome to Auto GitHub Uploader Bot!")
            return "OK", 200

        send_message(chat_id, "📤 Uploading...")

        compressed = compress_post(text)
        success = update_github_file(compressed)

        if success:
            send_message(chat_id, "✅ Uploaded successfully!")
        else:
            send_message(chat_id, "❌ Failed to upload. Please try again later.")
        return "Done", 200

    return "No text found", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
