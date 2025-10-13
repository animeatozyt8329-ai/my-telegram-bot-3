from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
import os
from keep_alive import keep_alive

# Get your bot token from Replit Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in environment variables")

# Function to delete message after a delay
async def delete_later(message, context, delay=300):  # 300 seconds = 5 minutes
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id
        )
    except Exception as e:
        # Ignore errors (like if already deleted or bot lacks permissions)
        pass

# Function to handle incoming messages
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg:  # if message is None, do nothing
        return

    if msg.sticker:  # Sticker detected
        asyncio.create_task(delete_later(msg, context, 300))
    elif msg.animation:  # GIF detected
        asyncio.create_task(delete_later(msg, context, 300))
    else:
        # Text or emojis → do nothing
        pass

# Main function to run the bot
def main():
    # Setup bot
    print("Building Telegram bot application...")
    app = Application.builder().token(TOKEN).build()

    # Handle all messages
    app.add_handler(MessageHandler(filters.ALL, handle_messages))

    keep_alive()   # Start the web server to keep alive
    print("Starting Telegram bot polling...")
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        print("Bot is running successfully!")
    except Exception as e:
        print(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    main()
