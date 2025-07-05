import logging
import os
import re
import aiohttp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simpan sementara URL TikTok dari user
user_links = {}

# Fungsi download video
async def download_tiktok_video(url: str) -> str:
    api_url = f"https://api.tiklydown.me/api/download?url={url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("video", {}).get("no_watermark")
            return None

# Fungsi download audio
async def download_tiktok_audio(url: str) -> str:
    api_url = f"https://api.tiklydown.me/api/download?url={url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("music")
            return None

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirimkan link video TikTok, nanti kamu bisa pilih mau unduh videonya atau audionya.")

# Handler pesan masuk
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    tiktok_url_pattern = r"https?://(www\.)?tiktok\.com/.+?video/.+"

    if re.match(tiktok_url_pattern, text):
        user_links[update.effective_user.id] = text
        keyboard = [
            [
                InlineKeyboardButton("🎬 Download Video", callback_data="video"),
                InlineKeyboardButton("🎵 Download Audio", callback_data="audio")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Pilih file yang ingin kamu unduh:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Kirimkan link video TikTok yang valid ya!")

# Handler untuk tombol
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    url = user_links.get(user_id)

    if not url:
        await query.edit_message_text("Link TikTok tidak ditemukan. Kirim ulang link videonya.")
        return

    if query.data == "video":
        await query.edit_message_text("Sedang mengunduh video...")
        video_url = await download_tiktok_video(url)
        if video_url:
            await context.bot.send_video(chat_id=query.message.chat_id, video=video_url, caption="✅ Berikut videonya tanpa watermark")
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Gagal mengunduh video. Coba lagi nanti.")

    elif query.data == "audio":
        await query.edit_message_text("Sedang mengunduh audio...")
        audio_url = await download_tiktok_audio(url)
        if audio_url:
            await context.bot.send_audio(chat_id=query.message.chat_id, audio=audio_url, caption="✅ Berikut audionya (MP3)")
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Gagal mengunduh audio. Coba lagi nanti.")

# Main
if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")  # Simpan token di .env atau export dulu
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot TikTok Downloader aktif!")
    app.run_polling()