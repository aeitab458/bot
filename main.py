from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters
import logging
import os

# --- Setup logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
# Environment variables with fallback to your provided values
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7567728588:AAHYkrfKBQC2uicLov63ho94g1LIj1O30CI")
ADMIN_UIDS = {7973112315, 903395157}  # Your admin UIDs
GROUP_ID = -1002672115790             # Your group ID
CHANNEL_ID = -1002310362731           # Your channel ID

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    await update.message.reply_text("🤖 Bot is ready! Send a video to forward.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for video messages"""
    try:
        if update.effective_user.id not in ADMIN_UIDS:
            await update.message.reply_text("❌ Unauthorized!")
            return

        video = update.message.video
        caption = f"{video.file_name or 'Untitled'} | {video.width}x{video.height}"
        
        # Forward to both group and channel
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
        logger.info(f"✅ Video forwarded: {caption}")

    except Exception as e:
        logger.error(f"🚨 Error handling video: {e}", exc_info=True)

def main():
    """Start the bot"""
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(
            filters.VIDEO & filters.User(ADMIN_UIDS), 
            handle_video
        ))
        
        logger.info("🚀 Bot is starting...")
        logger.info(f"👑 Admin UIDs: {ADMIN_UIDS}")
        logger.info(f"💬 Group ID: {GROUP_ID}")
        logger.info(f"📢 Channel ID: {CHANNEL_ID}")
        
        app.run_polling(
            non_stop=True,
            poll_interval=3,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"🔥 Failed to start bot: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
