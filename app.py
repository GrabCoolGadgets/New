import os
import requests
from flask import Flask, request
import base64

app = Flask(__name__)

# ✅ Tokens & Repo Info (already filled)
BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "allfls"  # File in root of main branch

# ✅ Compress the incoming post to one-line format
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

# ✅ Upload to GitHub
def update_github_file(new_entry):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("❌ Failed to get file:", res.text)
        return False

    content_data = res.json()
    sha = content_data["sha"]
    download_url = content_data["download_url"]
    existing = requests.get(download_url).text.strip()

    if new_entry in existing:
        print("⚠️ Duplicate. Skipping.")
        return True

    updated = (existing + "\n" + new_entry).strip()
    encoded = base64.b64encode(updated.encode()).decode()

    payload = {
        "message": "Auto Update from Telegram",
        "content": encoded,
        "sha": sha
    }

    put_res = requests.put(url, headers=headers, json=payload)
    print("✅ GitHub Update Status:", put_res.status_code)
    return put_res.status_code in [200, 201]

# ✅ Webhook Handler
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        compressed = compress_post(text)
        success = update_github_file(compressed)
        return "✅ Saved" if success else "❌ Failed", 200

    return "⚠️ No text found", 200

# ✅ Run Flask App (for Render or Replit)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
