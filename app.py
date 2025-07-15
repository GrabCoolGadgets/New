import os
from flask import Flask, request
from pymongo import MongoClient
import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["iPopcorn_Data"]
collection = db["posts"]

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        # Handle /start
        if text.lower() == "/start":
            send_message(chat_id, "👋 Welcome! Send me a post in the correct format.")
            return "ok", 200

        send_message(chat_id, "⏳ Uploading...")
        
        # Insert into MongoDB
        try:
            collection.insert_one({
                "text": text,
                "timestamp": datetime.datetime.utcnow()
            })
            send_message(chat_id, "✅ Successfully uploaded to MongoDB!")
        except Exception as e:
            send_message(chat_id, "❌ Failed to upload.")
            print("MongoDB Error:", str(e))
        
    return "ok", 200

def send_message(chat_id, text):
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route('/')
def home():
    return "Bot is running!", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
