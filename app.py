from flask import Flask, request
import requests
import json

app = Flask(__name__)

# ✅ Telegram Bot Token
BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ✅ Firebase Database URL
FIREBASE_URL = "https://tgjsn-3c09e-default-rtdb.firebaseio.com/posts.json"

# Welcome message on /start
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "🎉 Welcome! Send me any text and I will save it as a JSON entry in Firebase.")
        else:
            # ✅ Save post to Firebase
            firebase_res = requests.post(FIREBASE_URL, json={"text": text})

            if firebase_res.status_code == 200:
                send_message(chat_id, "✅ Post saved to Firebase successfully!")
            else:
                send_message(chat_id, "❌ Failed to save post to Firebase.")

    return "ok"

# Root route (optional)
@app.route("/", methods=["GET"])
def home():
    return "Bot is live!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
