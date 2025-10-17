import os
import asyncio
import time
from collections import deque
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters, CommandHandler
from keep_alive import keep_alive

# ======== CONFIG ========
TOKEN = os.environ.get("TELEGRAM_TOKEN")
DELETE_DELAY = 300       # 5 minutes
CHECK_INTERVAL = 10      # Check queue every 10 seconds for free plan

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in environment variables")

# ======== QUEUE ========
delete_queue = deque()  # store tuples (message, timestamp)

# ======== DELETION WORKER ========
async def delete_worker(context: ContextTypes.DEFAULT_TYPE):
    """Background task to delete messages in batches after delay"""
    while True:
        now = time.time()
        batch_count = 0
        while delete_queue and now - delete_queue[0][1] >= DELETE_DELAY:
            msg, _ = delete_queue.popleft()
            try:
                await context.bot.delete_message(
                    chat_id=msg.chat_id,
                    message_id=msg.message_id
                )
                batch_count += 1
            except Exception:
                pass  # Ignore if already deleted
        if batch_count > 0:
            print(f"🗑️ Deleted {batch_count} messages in this batch")
        await asyncio.sleep(CHECK_INTERVAL)  # low CPU usage for free plan

# ======== MESSAGE HANDLER ========
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    if msg.sticker or msg.animation:
        delete_queue.append((msg, time.time()))
        # No per-message logging to reduce Render free plan log spam

# ======== STATUS COMMAND ========
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len(delete_queue)
    await update.message.reply_text(f"📝 Messages queued for deletion: {count}")

# ======== MAIN FUNCTION ========
async def main():
    print("🚀 Starting Telegram bot (free-plan optimized)...")
    app = Application.builder().token(TOKEN).build()

    # Add handler for all messages
    app.add_handler(MessageHandler(filters.ALL, handle_messages))

    # Add /status command handler
    app.add_handler(CommandHandler("status", status))

    # Start keep-alive server for UptimeRobot ping
    keep_alive()
    print("🌐 Keep-alive server started")

    # Start background deletion worker
    app.job_queue.run_repeating(delete_worker, interval=CHECK_INTERVAL, first=1)

    print("✅ Telegram bot is now polling...")
    try:
        await app.run_polling(allowed_updates=Update.ALL_TYPES)
        print("🤖 Bot is running successfully!")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
