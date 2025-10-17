import os
import os
import threading
import time
from flask import Flask
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# ---------------------
# Configuration
# ---------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in environment variables")

# Keep-alive web server for Render
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# ---------------------
# Message deletion logic
# ---------------------
def delete_later(bot: Bot, chat_id: int, message_id: int, delay: int = 300):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass  # ignore errors

def handle_messages(update: Update, context: CallbackContext):
    msg = update.message
    if not msg:
        return

    if msg.sticker or msg.animation:
        # Start background deletion
        threading.Thread(target=delete_later, args=(context.bot, msg.chat_id, msg.message_id, 300)).start()
    # Text/emojis → do nothing

# ---------------------
# Main bot
# ---------------------
def main():
    # Start Flask in a separate thread
    threading.Thread(target=run_flask).start()
    print("✅ Keep-alive web server started!")

    # Telegram bot setup
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add message handler
    dp.add_handler(MessageHandler(Filters.all, handle_messages))

    # Start polling
    print("🚀 Bot is starting...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
