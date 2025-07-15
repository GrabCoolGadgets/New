from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Public Telegram Channel Username
CHANNEL_USERNAME = "iPopcornApp"

@app.route("/")
def home():
    return "✅ iPopcorn Telegram Scraper Running!"

@app.route("/posts")
def get_posts():
    try:
        url = f"https://t.me/s/{CHANNEL_USERNAME}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        posts = []
        for msg in soup.select(".tgme_widget_message_text"):
            text = msg.get_text(separator="\n").strip()
            if text:
                posts.append(text)

        return jsonify(posts[::-1])  # latest first

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
