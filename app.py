import os
import base64
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"  # inside 'main' branch

# === Format the incoming post ===
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

# === Update GitHub file ===
def update_github_file(new_entry):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("Failed to get file:", res.text)
        return False, "❌ GitHub file fetch failed"

    content_data = res.json()
    sha = content_data['sha']
    existing = requests.get(content_data['download_url']).text.strip()

    if new_entry in existing:
        print("Duplicate post")
        return True, "⚠️ Post already exists"

    updated = (existing + "\n" + new_entry).strip()

    payload = {
        "message": "Auto Update from Telegram",
        "content": base64.b64encode(updated.encode()).decode(),
        "sha": sha
    }

    res = requests.put(url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        print("✅ File updated on GitHub")
        return True, "✅ File uploaded successfully!"
    else:
        print("GitHub update failed:", res.text)
        return False, "❌ GitHub update failed"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    print("📩 Message received!")

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        compressed = compress_post(text)
        success, status_message = update_github_file(compressed)

        # send Telegram reply
        send_telegram_message(chat_id, status_message)
        return "Done", 200

    return "No text found", 200

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# === MAIN ENTRY ===
if __name__ == "__main__":
    print("🚀 Bot started and listening...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
