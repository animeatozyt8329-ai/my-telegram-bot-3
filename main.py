from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
import os
from keep_alive import keep_alive

# Get your bot token from environment variables
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
    except Exception:
        pass  # Ignore errors like message already deleted

# Function to handle incoming messages
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    if msg.sticker or msg.animation:
        asyncio.create_task(delete_later(msg, context, 300))
    # Other message types: ignore

# Main function to run the bot
def main():
    print("🚀 Building Telegram bot application...")
    app = Application.builder().token(TOKEN).build()

    # Add message handler
    app.add_handler(MessageHandler(filters.ALL, handle_messages))

    keep_alive()  # Keep-alive web server for Render

    print("✅ Starting Telegram bot polling...")
    try:
        # run_polling() is now asynchronous, so we use .run() instead
        app.run_polling()
        print("🤖 Bot is running successfully!")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        raise

if __name__ == "__main__":
    main()
