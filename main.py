# main.py

import threading
from flask import Flask, redirect, request
import telebot
from config import BOT_TOKEN, UPDATE_CHANNEL
from database import get_user, update_wallet
import time

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ========== FLASK LINK TRACKER ==========
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
                print(f"✅ User {uid} clicked {ad} → ₹{reward_map[ad]}")
        except Exception as e:
            print("❌ Click error:", e)

    redirect_map = {
        "cpm1": "https://gplinks.co/cpm1demo",
        "cpm2": "https://gplinks.co/cpm2demo",
        "cpm3": "https://gplinks.co/cpm3demo"
    }
    return redirect(redirect_map.get(ad, "https://t.me/Click2Earning_Pro"))

def start_flask():
    app.run(host="0.0.0.0", port=10000)

# ========== TELEGRAM BOT ==========
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.chat.id

    # Channel check
    try:
        chat_member = bot.get_chat_member(UPDATE_CHANNEL, user_id)
        if chat_member.status not in ['member', 'creator', 'administrator']:
            raise Exception("Not joined")
    except:
        join_btn = telebot.types.InlineKeyboardMarkup()
        join_btn.add(telebot.types.InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{UPDATE_CHANNEL[1:]}"))
        bot.send_message(user_id, "📢 Please join our update channel to use this bot.", reply_markup=join_btn)
        return

    get_user(user_id)

    menu = telebot.types.InlineKeyboardMarkup(row_width=2)
    menu.add(
        telebot.types.InlineKeyboardButton("📊 My Stats", callback_data="stats"),
        telebot.types.InlineKeyboardButton("💸 Earn Now", callback_data="earn"),
        telebot.types.InlineKeyboardButton("👥 My Referral Link", callback_data="referral"),
        telebot.types.InlineKeyboardButton("💼 Withdraw", callback_data="withdraw")
    )
    bot.send_message(user_id, "🎉 Welcome to Click2Earning Bot!\n👇 Choose an option:", reply_markup=menu)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    uid = call.from_user.id

    if call.data == "stats":
        user = get_user(uid)
        balance = user.get("wallet", 0.0)
        referrals = user.get("referrals", 0)
        earned = user.get("total_earned", 0.0)
        msg = f"📊 *Your Stats:*\n\n💰 Wallet: ₹{balance:.2f}\n👥 Referrals: {referrals}\n📈 Total Earned: ₹{earned:.2f}"
        bot.answer_callback_query(call.id)
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif call.data == "earn":
        base_url = "https://tgjsn.onrender.com"  # Replace with your actual Render URL
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            telebot.types.InlineKeyboardButton("💸 CPM $0.10 → ₹0.02", url=f"{base_url}/click?uid={uid}&ad=cpm1"),
            telebot.types.InlineKeyboardButton("💸 CPM $0.20 → ₹0.04", url=f"{base_url}/click?uid={uid}&ad=cpm2"),
            telebot.types.InlineKeyboardButton("💸 CPM $0.30 → ₹0.06", url=f"{base_url}/click?uid={uid}&ad=cpm3")
        )
        bot.answer_callback_query(call.id)
        bot.send_message(uid, "👇 Choose a task to earn:", reply_markup=markup)

    elif call.data == "referral":
        ref_link = f"https://t.me/Click2Earning_Pro_bot?start={uid}"
        msg = f"👥 *Your Referral Link:*\n\n🔗 {ref_link}\n\n🤑 You get ₹0.10 per valid referral!"
        bot.answer_callback_query(call.id)
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif call.data == "withdraw":
        bot.answer_callback_query(call.id)
        bot.send_message(uid, "💼 Withdraw system coming soon...")

# ========== RUN FLASK + BOT ==========
if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    print("🚀 Flask server running...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print("⚠️ Bot error:", e)
            time.sleep(5)
