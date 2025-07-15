import os
import base64
import requests
from flask import Flask, request

app = Flask(__name__)

# ✅ Replace with your actual tokens
BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"  # inside 'main' branch

# ✅ Format Telegram post into 1-line compressed form
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

# ✅ Update GitHub file with new data
def update_github_file(new_entry):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Fetch current file content
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("Failed to fetch file:", res.text)
        return False

    content_data = res.json()
    sha = content_data['sha']
    existing = requests.get(content_data['download_url']).text.strip()

    # Avoid duplicate posts
    if new_entry in existing:
        print("Duplicate post. Skipping.")
        return True

    updated = (existing + "\n" + new_entry).strip()

    payload = {
        "message": "Auto Update from Telegram",
        "content": base64.b64encode(updated.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }

    res = requests.put(url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        print("✅ GitHub file updated successfully.")
        return True
    else:
        print("❌ Failed to update GitHub:", res.text)
        return False

# ✅ Telegram Webhook Handler
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        compressed = compress_post(text)
        print("Incoming post:", compressed)
        success = update_github_file(compressed)
        return ("Saved" if success else "Failed"), 200

    return "No text found", 200

# ✅ Flask App Start
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
