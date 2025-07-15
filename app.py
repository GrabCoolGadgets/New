import os
import requests
import base64
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"  # main branch

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

# === Send message back to user ===
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

# === Upload to GitHub ===
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
    sha = content_data["sha"]
    existing = requests.get(content_data["download_url"]).text.strip()

    if new_entry in existing:
        print("⚠️ Duplicate post. Skipping.")
        return True

    updated = (existing + "\n" + new_entry).strip()

    base64_content = base64.b64encode(updated.encode()).decode()

    payload = {
        "message": "Auto Update from Telegram",
        "content": base64_content,
        "sha": sha
    }

    put_res = requests.put(url, headers=headers, json=payload)

    # ✅ Debug log
    print("=== GitHub PUT Response ===", put_res.status_code, put_res.text)

    return put_res.status_code in [200, 201]

# === Webhook endpoint ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]

        if "text" in message:
            text = message["text"]

            if text == "/start":
                send_telegram_message(chat_id, "👋 Welcome! Send me movie posts to upload to GitHub.")
                return "OK", 200

            send_telegram_message(chat_id, "⏳ Uploading...")

            compressed = compress_post(text)
            success = update_github_file(compressed)

            if success:
                send_telegram_message(chat_id, "✅ Successfully uploaded.")
            else:
                send_telegram_message(chat_id, "❌ Failed to upload. Please try again later.")

    return "OK", 200

# === Main ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
