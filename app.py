from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

CHANNEL_URL = "https://t.me/s/iPopcornApp"

@app.route('/')
def home():
    return 'Telegram Scraper Running ✅'

@app.route('/posts')
def get_posts():
    try:
        response = requests.get(CHANNEL_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')

        lines = []
        for msg in messages[:5]:  # latest 5 posts
            text = msg.get_text(separator="\n").strip()
            lines.extend(text.splitlines())

        return jsonify({"data": lines})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
