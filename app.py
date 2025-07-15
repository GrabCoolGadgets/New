import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"  # inside 'main' branch

# === Compress the post format ===
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

# === Upload to GitHub ===
def update_github_file(new_entry):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Step 1: Get existing file content
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("❌ GitHub file fetch failed:", res.status_code, res.text)
        return False

    content_data = res.json()
    sha = content_data['sha']
    existing = requests.get(content_data['download_url']).text.strip()

    # Avoid duplicates
    if new_entry in existing:
        print("⚠️ Duplicate post. Skipping.")
        return True

    updated = (existing + "\n" + new_entry).strip()
    base64_content = updated.encode("utf-8").decode("utf-8").encode("utf-8").hex()

    import base64
    encoded = base64.b64encode(updated.encode()).decode()

    payload = {
        "message": "Auto update from Telegram Bot",
        "content": encoded,
        "sha": sha
    }

    put_res = requests.put(url, headers=headers, json=payload)
    print("=== GitHub PUT Response ===", put_res.status_code, put_res.text)
    return put_res.status_code in [200, 201]

# === Webhook route ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            send_message(chat_id, "👋 Welcome! Send your post in proper format.")
            return "OK", 200

        send_message(chat_id, "⏳ Uploading to GitHub...")

        compressed = compress_post(text)
        success = update_github_file(compressed)

        if success:
            send_message(chat_id, "✅ Successfully uploaded!")
        else:
            send_message(chat_id, "❌ Failed to upload. Please try again later.")

    return "OK", 200

# === Telegram message sender ===
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

# === Main Entry ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
