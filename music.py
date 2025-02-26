import os
import logging
import tempfile

from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext
import yt_dlp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    """Send a welcome message when the /start command is issued."""
    update.message.reply_text(
        "Hello! I'm Lightning, your music bot. Use /play <song name or URL> to play a song."
    )

def play(update: Update, context: CallbackContext):
    """Download and send a song or video based on a query provided by the user."""
    if not context.args:
        update.message.reply_text("Please provide a song name or URL after /play.")
        return

    query = " ".join(context.args)
    message = update.message.reply_text("Processing your request, please wait...")
    chat_id = update.effective_chat.id

    # Send a chat action to let user know the bot is working
    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_AUDIO)

    # Create a temporary directory to store the downloaded file
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

                # Determine file type based on extension for sending appropriate media
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.mp3', '.m4a', '.webm', '.aac', '.ogg']:
                    update.message.reply_text(f"Sending audio: {file_title}")
                    context.bot.send_audio(
                        chat_id=chat_id,
                        audio=open(file_path, 'rb'),
                        title=file_title
                    )
                else:
                    update.message.reply_text(f"Sending video: {file_title}")
                    context.bot.send_video(
                        chat_id=chat_id,
                        video=open(file_path, 'rb'),
                        caption=file_title
                    )
        except Exception as e:
            logger.error("Error in play command: %s", e)
            update.message.reply_text("An error occurred while processing your request.")
        finally:
            try:
                message.delete()
            except Exception as e:
                logger.error("Failed to delete temporary message: %s", e)

def main():
    """Start the bot."""
    TOKEN = os.environ.get("7507720145:AAGwwmsLkfpNS0LlTbfVfIDKZXPUalZEDwE")
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        return

    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("play", play))

    # Start the Bot
    updater.start_polling()
    print("Bot is running...")
    updater.idle()

if __name__ == '__main__':
    main()
