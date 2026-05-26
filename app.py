import os
import logging
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get token from environment
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("❌ TELEGRAM_TOKEN environment variable not set!")
    # We'll still start Flask but bot won't work

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# ----- Handlers -----
def start(update, context):
    logger.info("Received /start command")
    update.message.reply_text("✅ Bot is working! Send me any message.")

def echo(update, context):
    logger.info(f"Echoing: {update.message.text}")
    update.message.reply_text(f"You said: {update.message.text}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ----- Flask routes -----
@app.route('/webhook', methods=['POST'])
def webhook():
    if not TOKEN:
        return jsonify({"error": "No token"}), 500
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.exception("Webhook error")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    if TOKEN:
        return f"Bot is running. Token present: {TOKEN[:5]}... (webhook endpoint: /webhook)"
    else:
        return "Error: TELEGRAM_TOKEN not set", 500

# ----- Main -----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    
    if TOKEN and host:
        webhook_url = f"https://{host}/webhook"
        try:
            bot.set_webhook(webhook_url)
            logger.info(f"✅ Webhook set to {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    elif TOKEN:
        logger.warning("RENDER_EXTERNAL_HOSTNAME not set, cannot set webhook automatically")
    else:
        logger.error("No token, webhook not set")
    
    app.run(host="0.0.0.0", port=port)
