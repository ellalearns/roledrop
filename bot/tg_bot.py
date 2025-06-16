from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import logging
from server.server import application
import json
from db.db import edit_user_categories, add_user_to_db


# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(messages)s",
#     level=logging.INFO
# )
# logging.getLogger("httpx").setLevel(logging.WARNING)
# logger = logging.getLogger(__name__)

categories_list = [
    "content writing",
    "software development",
    "virtual assistant",
    "customer service",
    "data entry",
    "design",
    "ai/ml engineering",
    "social media managment",
    "project management",
    "others"
]


keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Info", callback_data="info")],
    [InlineKeyboardButton("Edit", callback_data="edit")],
    [InlineKeyboardButton("Help", callback_data="help")],
    [InlineKeyboardButton("Pay", callback_data="pay")]
])

def get_user_category_keyboard(user_category_list):
    """
    return inline category keyboard based on user
    """
    
    def label(category):
        """
        """
        emoji = "✅" if category in user_category_list else "⬜"
        return emoji + " " + category
    
    buttons = []

    # buttons.append([InlineKeyboardButton("JOB CATEGORIES", callback_data="")])
    
    buttons.append([InlineKeyboardButton("JOB CATEGORIES", callback_data="NULL")])

    for category in categories_list:
        buttons.append(
            [InlineKeyboardButton(label(category), callback_data=f"toggle|{category}")]
            )

    buttons.append([InlineKeyboardButton("JOB SITES", callback_data="NULL")])
    buttons.append([InlineKeyboardButton("✅ LinkedIn", callback_data="NULL")])

    buttons.append([InlineKeyboardButton("🔽 Save", callback_data="save")])

    return InlineKeyboardMarkup(buttons)


site_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("LinkedIn", callback_data="")],
    [InlineKeyboardButton("Save", callback_data="")],
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    runs when user sends /start
    """
    user = update.effective_user
    await update.message.reply_text(f"Hi {user.first_name}")
    add_user_to_db(user.id)
    context.user_data["categories"] = set()
    await edit(update, context)


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    runs after /start
    or
    user runs /edit
    """
    user = update.effective_user
    await update.message.reply_text(f"Edit your job types and websites here. If your job type is not listed here, select others, it will be included there. We are working on grouping jobs better and adding more websites. Feel free to send suggestions to roledropapp@gmail.com", reply_markup=get_user_category_keyboard(context.user_data.setdefault("categories", set())))


async def button_handler(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    """
    """
    query = update.callback_query
    await query.answer()

    cmd = query.data

    if cmd.startswith("toggle|"):
        cat_key = cmd.split("|")[1]
        selected = context.user_data.get("categories", set())

        if cat_key in selected:
            selected.remove(cat_key)
        else:
            selected.add(cat_key)
        
        context.user_data["categories"] = selected

        markup = get_user_category_keyboard(selected)
        await query.edit_message_reply_markup(reply_markup=markup)
    
    elif cmd == "save":
        categories = context.user_data["categories"]
        cats = []
        for category in categories:
            cats.append(category)
        final_list = json.dumps(cats)
        edit_user_categories(final_list, update.effective_user.id)
        await query.edit_message_text("All Categories Saved")


def main_bot():
    """
    returns an instance of the roledrop bot
    """

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("edit", edit))

    application.add_handler(CallbackQueryHandler(button_handler))

    return application

