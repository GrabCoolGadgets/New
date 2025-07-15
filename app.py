import os
import base64
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"

# Format post
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

# Upload to GitHub
def update_github_file(new_entry):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("❌ GitHub file fetch failed:", res.text)
        return False

    content_data = res.json()
    sha = content_data['sha']
    existing = requests.get(content_data['download_url']).text.strip()

    if new_entry in existing:
        print("⚠️ Duplicate post. Skipping.")
        return True

    updated = (existing + "\n" + new_entry).strip()
    encoded_content = base64.b64encode(updated.encode("utf-8")).decode("utf-8")

    payload = {
        "message": "Auto Update from Telegram Bot",
        "content": encoded_content,
        "sha": sha
    }

    res = requests.put(url, headers=headers, json=payload)
    return res.status_code in [200, 201]

# Handle Telegram messages
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]

        if "text" in data["message"]:
            text = data["message"]["text"].strip()

            # Handle /start command
            if text.lower() == "/start":
                send_message(chat_id, "👋 Welcome to the GitHub Uploader Bot!\n\nSend your post in proper format to upload it to GitHub.")
                return "Start command processed", 200

            # Else, treat it as a post
            send_message(chat_id, "⏳ Uploading to GitHub...")
            compressed = compress_post(text)
            success = update_github_file(compressed)

            if success:
                send_message(chat_id, "✅ Successfully uploaded to GitHub!")
            else:
                send_message(chat_id, "❌ Failed to upload. Please try again later.")
            return "Processed post", 200

    return "No valid message found", 200

# Utility to send message to user
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = { "chat_id": chat_id, "text": text }
    requests.post(url, json=payload)

# Start app
if __name__ == "__main__":
    print("🚀 Bot is running...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
