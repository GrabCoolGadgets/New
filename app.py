from flask import Flask, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = '6355758949:AAEXMPJ9XnIr_sS-PqM7BiUaSFOrQd02oJE'
CHANNEL_USERNAME = 'iPopcornApp'

@app.route('/')
def home():
    return '✅ iPopcorn Movie Fetcher is Live!'

@app.route('/fetch')
def fetch():
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
    r = requests.get(url).json()

    movies = []
    for result in r.get("result", []):
        msg = result.get("message", {})
        if msg.get("chat", {}).get("username") == CHANNEL_USERNAME:
            text = msg.get("text", "")
            if "{" in text and "}" in text:
                movies.append(text.strip())

    return jsonify(movies)
