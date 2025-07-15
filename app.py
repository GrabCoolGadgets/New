import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
import telegram

# --- CONFIG ---
BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
MONGO_URI = "mongodb+srv://Ipopcorninline:Ipopcorninline@cluster0.8uues.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "iPopcorn App"
COLLECTION = "iPopcorn Data"

bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION]

# --- Compress post format ---
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

# --- TELEGRAM WEBHOOK ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        if "text" in data["message"]:
            text = data["message"]["text"]

            if text == "/start":
                bot.send_message(chat_id=chat_id, text="👋 Welcome to iPopcorn Bot!\nSend your post in the required format.")
                return "OK", 200

            bot.send_message(chat_id=chat_id, text="⏳ Uploading...")
            compressed = compress_post(text)

            if collection.find_one({"post": compressed}):
                bot.send_message(chat_id=chat_id, text="⚠️ Post already exists.")
            else:
                collection.insert_one({"post": compressed})
                bot.send_message(chat_id=chat_id, text="✅ Successfully uploaded.")

            return "OK", 200

    return "Ignored", 200

# --- API TO FETCH POSTS ---
@app.route("/posts", methods=["GET"])
def get_posts():
    data = collection.find({}, {"_id": 0})
    posts = [doc["post"] for doc in data]
    return jsonify({"data": posts})

# --- START APP ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
