# Main bot logic will go here

import threading
from flask import Flask, redirect, request
import telebot
from config import BOT_TOKEN, UPDATE_CHANNEL, ADMIN_ID
from database import get_user, update_wallet
import time

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- Flask Click Tracker ---
@app.route('/click')
def click():
    uid = request.args.get("uid")
    ad = request.args.get("ad")

    if uid and ad:
        try:
            uid = int(uid)
            reward_map = {
                "cpm1": 0.02,
                "cpm2": 0.04,
                "cpm3": 0.06
            }
            if ad in reward_map:
                update_wallet(uid, reward_map[ad])
        except:
            pass

    # Redirect to your CPM link
    redirect_map = {
        "cpm1": "https://gplinks.co/cpm1demo",
        "cpm2": "https://gplinks.co/cpm2demo",
        "cpm3": "https://gplinks.co/cpm3demo"
    }
    return redirect(redirect_map.get(ad, "https://t.me/Click2Earning_Pro"))

def start_flask():
    app.run(host="0.0.0.0", port=10000)

# --- Telegram Bot Commands ---
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.chat.id
    if not bot.get_chat_member(UPDATE_CHANNEL, user_id).status in ['member', 'creator', 'administrator']:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("✅ Joined", url=f"https://t.me/{UPDATE_CHANNEL[1:]}"))
        bot.send_message(user_id, "Please join our update channel to use this bot.", reply_markup=markup)
        return

    get_user(user_id)
    bot.send_message(user_id, "🎉 Welcome to Click2Earning Bot!\nUse /earn to get started!")

@bot.message_handler(commands=["earn"])
def handle_earn(message):
    uid = message.chat.id
    buttons = telebot.types.InlineKeyboardMarkup(row_width=1)
    buttons.add(
        telebot.types.InlineKeyboardButton("💸 CPM = $0.10 → ₹0.02", url=f"https://your-render-app.onrender.com/click?uid={uid}&ad=cpm1"),
        telebot.types.InlineKeyboardButton("💸 CPM = $0.20 → ₹0.04", url=f"https://your-render-app.onrender.com/click?uid={uid}&ad=cpm2"),
        telebot.types.InlineKeyboardButton("💸 CPM = $0.30 → ₹0.06", url=f"https://your-render-app.onrender.com/click?uid={uid}&ad=cpm3"),
    )
    bot.send_message(uid, "Choose any one offer below 👇", reply_markup=buttons)

@bot.message_handler(commands=["stats"])
def handle_stats(message):
    uid = message.chat.id
    user = get_user(uid)
    wallet = user.get("wallet", 0.0)
    bot.send_message(uid, f"💰 Your Wallet: ₹{wallet:.2f}")

# Start both Flask and Bot
if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Bot crashed: {e}")
            time.sleep(5)
