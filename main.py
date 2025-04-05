from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters
import logging
import os

# --- Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "7567728588:AAHYkrfKBQC2uicLov63ho94g1LIj1O30CI")  # Falls back to hardcoded if .env missing
ADMIN_UIDS = {7973112315, 903395157}
GROUP_ID = -1002672115790
CHANNEL_ID = -1002310362731

# --- Logging ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

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
            GROUP_ID, video.file_id, 
            caption=caption, 
            supports_streaming=True
        )
        await context.bot.send_video(
            CHANNEL_ID, video.file_id, 
            caption=caption, 
            supports_streaming=True
        )
        await update.message.delete()
        logger.info(f"✅ Video forwarded: {caption}")

    except Exception as e:
        logger.error(f"🚨 Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO & filters.User(ADMIN_UIDS), handle_video))
    
    # Non-stop polling with 3s interval
    app.run_polling(non_stop=True, poll_interval=3)

if __name__ == "__main__":
    main()