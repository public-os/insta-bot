import os
import yt_dlp
import tempfile
import shutil
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")

COOKIES_FILE = "cookies.txt"   # Instagram login cookies

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ============================================


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Send any Instagram Reel / Video link."
    )


# Download function
def download_instagram(url):

    temp_dir = tempfile.mkdtemp()

    ydl_opts = {
        # Best video + audio
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",

        # Output
        "outtmpl": f"{temp_dir}/video.%(ext)s",

        # Cookies (LOGIN SUPPORT)
        "cookiefile": COOKIES_FILE,

        # Network
        "socket_timeout": 60,
        "retries": 5,

        # Logs
        "quiet": False,
        "verbose": True,

        # Other
        "noplaylist": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=True)

        file_path = ydl.prepare_filename(info)

    return file_path, temp_dir


# Handle messages
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    url = update.message.text.strip()

    # Validate link
    if "instagram.com" not in url:
        await update.message.reply_text("❌ Send a valid Instagram link.")
        return

    wait_msg = await update.message.reply_text("⏳ Downloading...")

    try:
        file_path, folder = download_instagram(url)

        # Send video
        with open(file_path, "rb") as video:
            await update.message.reply_video(
                video=video,
                caption="✅ Downloaded via Insta Bot 🤖"
            )

        # Cleanup
        shutil.rmtree(folder)

        await wait_msg.delete()

    except Exception as e:

        await wait_msg.delete()

        await update.message.reply_text(
            "❌ Download failed.\n"
            "Try another public link."
        )

        print("DOWNLOAD ERROR:", e)


# Main
def main():

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in ENV")
        return

    if not os.path.exists(COOKIES_FILE):
        print("❌ cookies.txt not found!")
        print("⚠️ Upload Instagram cookies first")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🤖 Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()