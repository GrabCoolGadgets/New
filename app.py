import telebot
from flask import Flask, jsonify, request

BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
CHANNEL_USERNAME = "iPopcornApp"  # बस username, बिना https://t.me/

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)
posts = []

@bot.channel_post_handler(func=lambda message: True)
def handle_channel_post(message):
    if message.chat.username == CHANNEL_USERNAME:
        text = message.text
        posts.insert(0, text)
        if len(posts) > 100:
            posts.pop()

@app.route("/")
def home():
    return "Bot is live!"

@app.route("/posts")
def get_posts():
    return jsonify(posts)

if __name__ == "__main__":
    bot.infinity_polling()
