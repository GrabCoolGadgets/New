from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

# 🔐 Your Telegram Bot Token & Firebase URL
BOT_TOKEN = "6355758949:AAFF__i3fAuQEGps_gj7i-InIk9f7dNgjWM"
FIREBASE_URL = "https://tgjsn-3c09e-default-rtdb.firebaseio.com"

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Send me your post in the format:\n\nTag {line1, line2}")

# ✅ Save to Firebase
def save_to_firebase(tag, content):
    data = {
        "tag": tag,
        "content": content
    }
    res = requests.post(f"{FIREBASE_URL}/posts.json", json=data)
    if res.status_code == 200:
        return True
    else:
        print("Firebase Error:", res.text)
        return False

# ✅ Handle post message
async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text("📤 Uploading...")

    if "{" in msg and "}" in msg:
        try:
            tag = msg.split("{")[0].strip().strip('"')
            content_block = msg.split("{")[1].split("}")[0]
            content_lines = [line.strip() for line in content_block.split(",") if line.strip()]
            formatted_content = ", ".join(content_lines)

            success = save_to_firebase(tag, formatted_content)
            if success:
                await update.message.reply_text("✅ Post saved to Firebase!")
            else:
                await update.message.reply_text("❌ Failed to save. Please try again.")
        except Exception as e:
            print("Parsing Error:", e)
            await update.message.reply_text("⚠️ Format error. Use: Tag {line1, line2}")
    else:
        await update.message.reply_text("⚠️ Format error. Use: Tag {line1, line2}")

# ✅ Start bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_post))

    print("🤖 Bot started...")
    app.run_polling()
