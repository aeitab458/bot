from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters
import logging
import os
from flask import Flask
from threading import Thread

# Initialize Flask server
server = Flask(__name__)

@server.route('/')
def health_check():
    return "Bot is alive and running!", 200

# --- Configuration ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7567728588:AAHYkrfKBQC2uicLov63ho94g1LIj1O30CI")  # Remove hardcoded token in production
ADMIN_UIDS = {7973112315, 903395157}
GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID", "-1002672115790"))
CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID", "-1002310362731"))

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is ready! Send a video to forward.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_UIDS:
            await update.message.reply_text("❌ Unauthorized!")
            return

        video = update.message.video
        caption = f"{video.file_name or 'Untitled'} | {video.width}x{video.height}"
        
        await context.bot.send_video(
            GROUP_ID,
            video.file_id,
            caption=caption,
            supports_streaming=True
        )
        await context.bot.send_video(
            CHANNEL_ID,
            video.file_id,
            caption=caption,
            supports_streaming=True
        )
        await update.message.delete()
        logging.info(f"✅ Video forwarded: {caption}")

    except Exception as e:
        logging.error(f"🚨 Error handling video: {e}", exc_info=True)

def run_flask():
    port = int(os.getenv("PORT", 8080))  # Default to 8080 if PORT not set
    server.run(host='0.0.0.0', port=port)

def main():
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start Telegram bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.VIDEO & filters.User(ADMIN_UIDS),
        handle_video
    ))
    
    logging.info("🚀 Bot starting...")
    logging.info(f"👑 Admin UIDs: {ADMIN_UIDS}")
    logging.info(f"💬 Group ID: {GROUP_ID}")
    logging.info(f"📢 Channel ID: {CHANNEL_ID}")
    
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
