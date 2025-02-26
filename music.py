import os
import logging
import tempfile
import asyncio
import os.path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp
import nest_asyncio

# Apply nest_asyncio to allow nesting event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Hello! I'm Lightning, your music bot. Use /play <song name or URL> to play a song."
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download and send a song or video based on a query provided by the user."""
    if not context.args:
        await update.message.reply_text("Please provide a song name or URL after /play.")
        return

    query = " ".join(context.args)
    message = await update.message.reply_text("Processing your request, please wait...")
    chat_id = update.effective_chat.id

    # Let the user know the bot is working
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_AUDIO)

    # Create a temporary directory for the downloaded file
    with tempfile.TemporaryDirectory() as tmp_dir:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # If the query is not a URL, perform a YouTube search
                if not query.startswith("http"):
                    query = "ytsearch:" + query
                info = ydl.extract_info(query, download=True)

                # If it's a search result, get the first entry
                if 'entries' in info:
                    info = info['entries'][0]

                file_path = ydl.prepare_filename(info)
                file_title = info.get('title', 'Unknown Title')

                # Determine file type based on extension
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.mp3', '.m4a', '.webm', '.aac', '.ogg']:
                    await update.message.reply_text(f"Sending audio: {file_title}")
                    await context.bot.send_audio(
                        chat_id=chat_id,
                        audio=open(file_path, 'rb'),
                        title=file_title
                    )
                else:
                    await update.message.reply_text(f"Sending video: {file_title}")
                    await context.bot.send_video(
                        chat_id=chat_id,
                        video=open(file_path, 'rb'),
                        caption=file_title
                    )
        except Exception as e:
            logger.error("Error in play command: %s", e)
            await update.message.reply_text("An error occurred while processing your request.")
        finally:
            try:
                await message.delete()
            except Exception as e:
                logger.error("Failed to delete temporary message: %s", e)

async def main():
    """Start the bot."""
    TOKEN = "7507720145:AAGwwmsLkfpNS0LlTbfVfIDKZXPUalZEDwE"
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        return

    # Build the application using the new asynchronous framework
    application = ApplicationBuilder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))

    print("Bot is running...")
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
