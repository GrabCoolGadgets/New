# Flask link tracker code will go here

from flask import Flask, redirect, request
from database import update_wallet
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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
                print(f"✅ User {uid} clicked {ad} → Earned ₹{reward_map[ad]}")
        except Exception as e:
            print("Error in click route:", e)

    redirect_map = {
        "cpm1": "https://gplinks.co/cpm1demo",
        "cpm2": "https://gplinks.co/cpm2demo",
        "cpm3": "https://gplinks.co/cpm3demo"
    }

    return redirect(redirect_map.get(ad, "https://t.me/Click2Earning_Pro"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
