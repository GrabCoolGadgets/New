import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = os.getenv("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")
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"

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
        print("⚠️ Duplicate post. Skipping.")
        return True

    updated = (existing + "\n" + new_entry).strip()
    encoded_content = updated.encode("utf-8")
    import base64
    base64_content = base64.b64encode(encoded_content).decode("utf-8")

    payload = {
        "message": "Auto Update from Telegram",
        "content": base64_content,
        "sha": sha
    }

    put_res = requests.put(url, headers=headers, json=payload)
    print("=== GitHub PUT Response ===", put_res.status_code, put_res.text)
    return put_res.status_code in [200, 201]

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        if "text" in data["message"]:
            text = data["message"]["text"]

            if text == "/start":
                send_message(chat_id, "👋 Welcome to Movie Uploader Bot!")
                return "Started", 200

            send_message(chat_id, "⏳ Uploading to GitHub...")
            compressed = compress_post(text)
            success = update_github_file(compressed)
            if success:
                send_message(chat_id, "✅ Uploaded Successfully to GitHub!")
            else:
                send_message(chat_id, "❌ Upload failed.")
            return "Done", 200

    return "No text", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
