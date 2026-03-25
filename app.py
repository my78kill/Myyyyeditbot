import asyncio
from flask import Flask
from threading import Thread

from pyrogram import Client, filters
from pyrogram.types import Message

# 🔑 CONFIG
API_ID = 30952267
API_HASH = "d87301a4bf06b8c040db8628900271cd"
BOT_TOKEN = "8547971593:AAEFw40CdcUO2r9SKnIjYBj6T-y3-myu0hU"

# 🤖 Bot Client
bot = Client("EditGuardianBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🌐 Flask App (for Render)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# ▶️ Start bot in separate thread
def run_bot():
    bot.run()

# /start command (DM welcome)
@bot.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        f"👋 Hello {message.from_user.mention}!\n\n"
        "🤖 I am an Edit Guardian Bot.\n"
        "📌 I automatically delete edited messages in groups.\n\n"
        "⚠️ Do not edit messages 😉"
    )

# 🛑 Edited message handler
@bot.on_edited_message(filters.group)
async def edited_handler(client, message: Message):
    try:
        user = message.from_user
        if not user:
            return

        mention = user.mention

        # ⚠️ Warning message
        warn_msg = await message.reply_text(
            f"⚠️ {mention}, your edited message will be deleted in 30 minutes."
        )

        # Delete warning after 10 sec
        await asyncio.sleep(10)
        await warn_msg.delete()

        # Delete original edited message after remaining time
        await asyncio.sleep(1790)
        await message.delete()

    except Exception as e:
        print(e)

# 🚀 Run both Flask + Bot
if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=5000)
