from flask import Flask, request
from telegram import Bot
from pymongo import MongoClient
from sync_mongo_to_github import format_posts, update_github_file

app = Flask(__name__)

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
MONGO_URI = "mongodb+srv://Ipopcorninline:Ipopcorninline@cluster0.8uues.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["iPopcornApp"]
collection = db["iPopcornData"]

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip().lower()

        bot = Bot(token=BOT_TOKEN)

        if text == "/start":
            bot.send_message(chat_id, "👋 Welcome! Type /update to sync data to GitHub.")
        elif text == "/update":
            bot.send_message(chat_id, "🔄 Uploading to GitHub...")
            posts = list(collection.find())
            formatted = format_posts(posts)
            update_github_file(formatted)
            bot.send_message(chat_id, "✅ GitHub Updated Successfully!")

    return "OK", 200
