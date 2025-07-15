import os
import requests
import base64
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"  # 👈 no .txt

# Format incoming Telegram message
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

# Get GitHub file content & sha
def get_github_content():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        content = requests.get(data['download_url']).text.strip()
        return content, data['sha']
    else:
        print("❌ GitHub file fetch failed:", res.status_code, res.text)
        return None, None

# Upload to GitHub
def update_github_file(new_entry):
    existing, sha = get_github_content()
    if existing is None:
        return False

    if new_entry in existing:
        print("⚠️ Duplicate post. Skipping.")
        return True

    updated = (existing + "\n" + new_entry).strip()
    b64_content = base64.b64encode(updated.encode()).decode()

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    payload = {
        "message": "Auto Update from Telegram",
        "content": b64_content,
        "sha": sha
    }

    res = requests.put(url, headers=headers, json=payload)
    print("=== GitHub PUT Response ===", res.status_code, res.text)
    return res.status_code in [200, 201]

# Telegram webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    if message.get("text") == "/start":
        send_telegram(chat_id, "👋 Welcome! Send a post and I’ll save it to GitHub.")
        return "OK", 200

    if "text" in message:
        text = message["text"]
        send_telegram(chat_id, "📤 Uploading...")
        compressed = compress_post(text)
        success = update_github_file(compressed)
        if success:
            send_telegram(chat_id, "✅ Successfully uploaded!")
        else:
            send_telegram(chat_id, "❌ Failed to upload. Please try again later.")
        return "OK", 200

    return "No text", 200

# Function to send message via Telegram bot
def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# Start app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
