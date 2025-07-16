import telebot

BOT_TOKEN = "8149705514:AAHTICcuHg7n6Qd5c-b7wBvCKbLWEImWx80"  # Apna current bot token

bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()
print("✅ Webhook removed successfully.")
