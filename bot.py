import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import subprocess
import os
import uuid

TOKEN = "ISI_TOKEN_KAMU_DI_SINI"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def download_tiktok(url: str) -> str | None:
    video_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.mp4")
    try:
        result = subprocess.run(
            ["yt-dlp", "-o", output_path, url],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
        else:
            logger.error(result.stderr)
            return None
    except Exception as e:
        logger.error(f"Download error: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "tiktok.com" in text:
        await update.message.reply_text("⏳ Mengunduh video TikTok...")
        video_path = await download_tiktok(text)
        if video_path:
            await update.message.reply_video(video=open(video_path, "rb"))
            os.remove(video_path)
        else:
            await update.message.reply_text("❌ Gagal mengunduh video. Pastikan link valid.")
    else:
        await update.message.reply_text("❗ Kirimkan link video TikTok yang ingin kamu unduh.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
