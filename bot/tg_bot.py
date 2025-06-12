from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import logging
from server.server import application


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(messages)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    runs when user sends /start
    """
    user = update.effective_user
    await update.message.reply_text(f"Hi {user.first_name}")


def main_bot():
    """
    returns an instance of the roledrop bot
    """

    application.add_handler(CommandHandler("start", start))

    return application

