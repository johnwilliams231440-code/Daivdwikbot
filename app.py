import os
import sys
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# Force print to flush immediately
sys.stdout.reconfigure(line_buffering=True)

print("🚀 Starting app.py...")

app = Flask(__name__)

# Get token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
print(f"🔑 TELEGRAM_TOKEN present: {bool(TOKEN)}")
if not TOKEN:
    print("❌ ERROR: TELEGRAM_TOKEN environment variable not set!")
else:
    print(f"✅ Token found (first 5 chars): {TOKEN[:5]}...")

if TOKEN:
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher(bot, None, use_context=True)

    def start(update, context):
        print("📨 Received /start command")
        update.message.reply_text("✅ Bot is alive! Send me any message.")

    def echo(update, context):
        print(f"📨 Echo: {update.message.text}")
        update.message.reply_text(f"You said: {update.message.text}")

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    @app.route('/webhook', methods=['POST'])
    def webhook():
        print("🔔 Webhook called")
        if not TOKEN:
            return jsonify({"error": "No token"}), 500
        try:
            update = Update.de_json(request.get_json(force=True), bot)
            dispatcher.process_update(update)
            return jsonify({"status": "ok"})
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    if TOKEN:
        return f"✅ Bot running. Token starts with {TOKEN[:5]}..."
    else:
        return "❌ TELEGRAM_TOKEN not set", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    print(f"🌐 Host: {host}, Port: {port}")

    if TOKEN and host:
        webhook_url = f"https://{host}/webhook"
        try:
            bot.set_webhook(webhook_url)
            print(f"✅ Webhook set to {webhook_url}")
        except Exception as e:
            print(f"❌ Failed to set webhook: {e}")
    elif TOKEN and not host:
        print("⚠️ RENDER_EXTERNAL_HOSTNAME not set – cannot set webhook")
    else:
        print("⚠️ No token, skipping webhook setup")

    print("🏃 Starting Flask server...")
    app.run(host="0.0.0.0", port=port)
