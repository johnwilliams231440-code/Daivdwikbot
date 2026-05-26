import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------- Flask app for health check ----------
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is running", 200

# ---------- Bot handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive! Send me any text and I'll echo it.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

# ---------- Main function to run bot ----------
async def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("❌ TELEGRAM_TOKEN environment variable not set!")
        return

    # Create application
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start polling (no webhooks)
    print("🤖 Bot started, polling...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Keep running
    await asyncio.Event().wait()

# ---------- Run both Flask and bot in a single event loop ----------
if __name__ == "__main__":
    import threading
    from telegram.ext import filters, MessageHandler

    def run_bot():
        asyncio.run(main())

    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Run Flask (will block main thread)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
