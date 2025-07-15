from flask import Flask, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
CHANNEL_USERNAME = "iPopcornApp"

def extract_posts(messages):
    posts = []
    for msg in messages:
        if 'text' in msg:
            text = msg['text']
            if '{' in text and '}' in text:
                parts = text.split('{', 1)
                title = parts[0].strip()
                content = parts[1].rsplit('}', 1)[0].strip()
                posts.append({
                    "name": title,
                    "details": content,
                    "fullText": (title + ' ' + content).lower()
                })
    return posts

@app.route("/")
def home():
    return "✅ API is running!"

@app.route("/movies")
def get_movies():
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        res = requests.get(url)
        data = res.json()
        
        if not data["ok"]:
            return jsonify({"error": "Failed to fetch messages"}), 500

        messages = [msg["message"] for msg in data["result"] if "message" in msg]
        movies = extract_posts(messages)
        return jsonify(movies)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
