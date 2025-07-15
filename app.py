import os
import base64
import requests
from flask import Flask, request

app = Flask(__name__)

# === CONFIGURATION ===
BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "data/posts.txt"  # Yeh file GitHub me already honi chahiye

# === FUNCTION: Compress post to single line ===
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

# === FUNCTION: Upload to GitHub ===
def upload_to_github(new_entry):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("❌ GitHub file fetch failed")
        return False

    content_data = res.json()
    sha = content_data.get('sha')
    existing_content = requests.get(content_data['download_url']).text.strip()

    # Avoid duplicate post
    if new_entry in existing_content:
        print("⚠️ Duplicate post skipped")
        return True

    updated_content = existing_content + "\n" + new_entry
    encoded = base64.b64encode(updated_content.encode()).decode()

    payload = {
        "message": "Auto update from Telegram bot",
        "content": encoded,
        "sha": sha
    }

    put_res = requests.put(url, headers=headers, json=payload)
    print("=== GitHub PUT Response ===", put_res.status_code, put_res.text)
    return put_res.status_code in [200, 201]

# === ROUTE: Telegram Webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            send_msg(chat_id, "👋 Welcome! Send me movie post text and I’ll upload to GitHub.")
            return "OK", 200

        send_msg(chat_id, "⏳ Uploading to GitHub...")
        compressed = compress_post(text)
        success = upload_to_github(compressed)

        if success:
            send_msg(chat_id, "✅ Successfully uploaded to GitHub!")
        else:
            send_msg(chat_id, "❌ Failed to upload. Try again later.")
    return "OK", 200

# === FUNCTION: Send message to Telegram ===
def send_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# === MAIN ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
