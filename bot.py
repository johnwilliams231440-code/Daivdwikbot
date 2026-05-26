import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import json

# === CONFIGURATION ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"        # From BotFather
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"   # From platform.openai.com

# === START COMMAND ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎨 Hi! Send me a text description and I'll generate an image for you.\n\n"
        "Example: 'a cute cat wearing sunglasses'"
    )

# === IMAGE GENERATION ===
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("🎨 Generating your image... please wait.")
    
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                image_url = result['data'][0]['url']
                await update.message.reply_photo(image_url, caption=f"🎨 Generated for: {prompt}")
            else:
                await update.message.reply_text("❌ Failed to generate image. Please try again.")

# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))
    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
