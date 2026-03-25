import telebot
import os
import json
import time
import threading
from telebot import types
import main  # Flask file

# Bot config
TOKEN = "8547971593:AAEFw40CdcUO2r9SKnIjYBj6T-y3-myu0hU"

# Owner + Friends IDs
SUPER_ADMINS = [8084941586, 8673593109]

bot = telebot.TeleBot(TOKEN)

# Files
AUTH_FILE = "auth.json"
EDIT_AUTH_FILE = "auth_edit.json"
PUNISH_FILE = "punish.json"
DELAY_FILE = "delay.json"
DELAY_POWER_FILE = "delay_power.json"

# Utils
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def get_user_id(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
    parts = message.text.split()
    if len(parts) > 1 and parts[1].isdigit():
        return int(parts[1])
    return None

# Load data
auth_users = load_json(AUTH_FILE)
auth_edit_users = load_json(EDIT_AUTH_FILE)
punished_users = load_json(PUNISH_FILE)
delay_power_users = load_json(DELAY_POWER_FILE)
delay_time = load_json(DELAY_FILE)
delay_time = delay_time if isinstance(delay_time, int) else 10

AUTHORIZED_PUNISH_USERS = SUPER_ADMINS

# Start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    name = message.from_user.first_name
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📜 Commands", callback_data="show_commands")
    markup.add(btn)
    bot.send_message(message.chat.id, f"Hello 👋 and welcome 🥂 {name}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "show_commands")
def show_commands(call):
    bot.send_message(call.message.chat.id, """
Available Commands:
/auth /unauth
/authedit /unauthedit
/punish /unpunish
/powerdelay
/setdely [10s/1m/30s]
""")

# Auth
@bot.message_handler(commands=["auth", "unauth"])
def handle_auth(message):
    uid = get_user_id(message)
    if uid:
        if message.text.startswith("/auth"):
            if uid not in auth_users:
                auth_users.append(uid)
                save_json(AUTH_FILE, auth_users)
                bot.send_message(message.chat.id, f"✅ User {uid} authorized for media.")
        else:
            if uid in auth_users:
                auth_users.remove(uid)
                save_json(AUTH_FILE, auth_users)
                bot.send_message(message.chat.id, f"❌ User {uid} removed from media auth.")
    else:
        bot.reply_to(message, "Reply to a message or use /auth user_id")

# Edit Auth
@bot.message_handler(commands=["authedit", "unauthedit"])
def handle_auth_edit(message):
    uid = get_user_id(message)
    if uid:
        if message.text.startswith("/authedit"):
            if uid not in auth_edit_users:
                auth_edit_users.append(uid)
                save_json(EDIT_AUTH_FILE, auth_edit_users)
                bot.send_message(message.chat.id, f"✅ User {uid} allowed to edit messages.")
        else:
            if uid in auth_edit_users:
                auth_edit_users.remove(uid)
                save_json(EDIT_AUTH_FILE, auth_edit_users)
                bot.send_message(message.chat.id, f"❌ User {uid} no longer allowed to edit.")
    else:
        bot.reply_to(message, "Reply to a message or use /authedit user_id")

# Punish
@bot.message_handler(commands=["punish", "unpunish"])
def handle_punish(message):
    if message.from_user.id not in AUTHORIZED_PUNISH_USERS:
        return
    uid = get_user_id(message)
    if uid:
        if message.text.startswith("/punish"):
            if uid not in punished_users:
                punished_users.append(uid)
                save_json(PUNISH_FILE, punished_users)
                bot.send_message(message.chat.id, f"🚫 User {uid} punished globally.")
        else:
            if uid in punished_users:
                punished_users.remove(uid)
                save_json(PUNISH_FILE, punished_users)
                bot.send_message(message.chat.id, f"✅ User {uid} unpunished globally.")
    else:
        bot.reply_to(message, "Reply to a message or use /punish user_id")

# Power Delay
@bot.message_handler(commands=["powerdelay"])
def grant_delay_power(message):
    uid = get_user_id(message)
    if uid:
        if uid not in delay_power_users:
            delay_power_users.append(uid)
            save_json(DELAY_POWER_FILE, delay_power_users)
            bot.send_message(message.chat.id, f"✅ User {uid} granted /setdely permission.")
    else:
        bot.reply_to(message, "Reply to a user or give ID")

# Set Delay
@bot.message_handler(commands=["setdely"])
def set_delay_time(message):
    if message.from_user.id not in delay_power_users + SUPER_ADMINS:
        return
    parts = message.text.split()
    if len(parts) >= 2:
        t = parts[1].lower()
        try:
            if t.endswith("s"):
                val = int(t[:-1])
            elif t.endswith("m"):
                val = int(t[:-1]) * 60
            else:
                val = int(t)
            global delay_time
            delay_time = val
            save_json(DELAY_FILE, delay_time)
            bot.send_message(message.chat.id, f"⏳ Media delete delay set to {val} seconds.")
        except:
            bot.send_message(message.chat.id, "Invalid format")

# ✅ EDITED MESSAGE SYSTEM (YOUR FEATURE)
@bot.edited_message_handler(func=lambda m: True)
def delete_edited(m):
    if m.from_user.id in auth_edit_users:
        return

    try:
        user = m.from_user
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

        warn = bot.send_message(
            m.chat.id,
            f"⚠️ {mention}, your edited message will be deleted in 30 minutes.",
            parse_mode="HTML"
        )

        def delete_warn():
            time.sleep(10)
            try:
                bot.delete_message(m.chat.id, warn.message_id)
            except:
                pass

        threading.Thread(target=delete_warn).start()

        def delete_original():
            time.sleep(1800)
            try:
                bot.delete_message(m.chat.id, m.message_id)
            except:
                pass

        threading.Thread(target=delete_original).start()

    except Exception as e:
        print(e)

# Media delete
def media_delete_later(chat_id, msg_id, user_id):
    if user_id in auth_users:
        return
    time.sleep(delay_time)
    try:
        bot.delete_message(chat_id, msg_id)
    except:
        pass

@bot.message_handler(content_types=["photo", "video", "audio", "sticker", "voice", "document", "animation"])
def handle_media(message):
    if message.from_user.id in punished_users:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        return
    threading.Thread(target=media_delete_later, args=(message.chat.id, message.message_id, message.from_user.id)).start()

@bot.message_handler(func=lambda m: True)
def auto_delete_if_punished(message):
    if message.from_user.id in punished_users:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

# ✅ Flask runner (FIXED)
def run_flask():
    main.app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_flask).start()

print("Bot is running...")
bot.infinity_polling()
