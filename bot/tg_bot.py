from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
import logging
from server.server import application


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(messages)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Info", callback_data="info")],
    [InlineKeyboardButton("Edit", callback_data="edit")],
    [InlineKeyboardButton("Help", callback_data="help")],
    [InlineKeyboardButton("Pay", callback_data="pay")]
])

category_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("content writing", callback_data="toggle_writing")],
    [InlineKeyboardButton("software development", callback_data="toggle_dev")],
    [InlineKeyboardButton("virtual assistant", callback_data="toggle_assitant")],
    [InlineKeyboardButton("customer service", callback_data="toggle_service")],
    [InlineKeyboardButton("data entry", callback_data="toggle_data")],
    [InlineKeyboardButton("design", callback_data="toggle_design")],
    [InlineKeyboardButton("ai/ml engineering", callback_data="toggle_ml")],
    [InlineKeyboardButton("social media management", callback_data="toggle_social")],
    [InlineKeyboardButton("project management", callback_data="toggle_project")],
    [InlineKeyboardButton("others", callback_data="toggle_others")],
    [InlineKeyboardButton("Save", callback_data="save")],
])

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

