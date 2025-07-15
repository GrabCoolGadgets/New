from flask import Flask, request
from telegram import Bot
from pymongo import MongoClient
import requests
import base64

app = Flask(__name__)

# ✅ Configuration
BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
MONGO_URI = "mongodb+srv://Ipopcorninline:Ipopcorninline@cluster0.8uues.mongodb.net/"
GITHUB_TOKEN = "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"
REPO = "GrabCoolGadgets/ip"
FILE_PATH = "data/posts.txt"  # GitHub repo path

# ✅ MongoDB connection
client = MongoClient(MONGO_URI)
db = client["iPopcornApp"]
collection = db["iPopcornData"]

# ✅ Format MongoDB posts into single-line GitHub format
def format_posts(posts):
    result = ""
    for post in posts:
        if "text" in post:
            lines = [line.strip() for line in post["text"].split('\n') if line.strip()]
            compressed = ""
            for i, line in enumerate(lines):
                if line.endswith("{"):
                    compressed += lines[i].replace("{", "") + "{"
                elif line == "}":
                    compressed += "}"
                else:
                    compressed += line + " "
            result += compressed.strip() + "\n"
    return result.strip()

# ✅ Update GitHub File
def update_github_file(new_content):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("❌ GitHub file fetch failed")
        return False

    sha = res.json().get('sha', None)
    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": "Updated from MongoDB via Telegram Bot",
        "content": encoded_content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    put_res = requests.put(url, headers=headers, json=payload)
    print("✅ GitHub Update:", put_res.status_code, put_res.text)
    return put_res.status_code in [200, 201]

# ✅ Telegram Bot Handler
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"].strip().lower()
        chat_id = data["message"]["chat"]["id"]
        bot = Bot(token=BOT_TOKEN)

        if text == "/start":
            bot.send_message(chat_id, "👋 Welcome! Send /update to sync posts to GitHub.")
        elif text == "/update":
            bot.send_message(chat_id, "🔄 Uploading posts to GitHub...")
            posts = list(collection.find())
            formatted = format_posts(posts)
            success = update_github_file(formatted)
            if success:
                bot.send_message(chat_id, "✅ GitHub Updated Successfully!")
            else:
                bot.send_message(chat_id, "❌ Failed to upload. Please try again later.")
        else:
            bot.send_message(chat_id, "❓ Unknown command. Type /update to push data.")

    return "OK", 200

# ✅ Start Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
