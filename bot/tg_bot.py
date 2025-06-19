from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from server.server import application
import json
from db.db import edit_user_categories, add_user_to_db, verify_subscription, delete_user_by_id, check_user, get_user_info
from telegram.error import Forbidden, TimedOut
from telegram.constants import ParseMode
from dotenv import load_dotenv
import os
from deps.deps import make_payment
import email_validator


load_dotenv(override=True)
token = os.getenv("BOT_TOKEN")
secret_key = os.getenv("SECRET_KEY")
payment_gateway = os.getenv("PAYMENT_GATEWAY")
content_type = os.getenv("CONTENT_TYPE")
amount = os.getenv("AMOUNT")
complete_payment = os.getenv("COMPLETE_PAYMENT")


ASK_EMAIL = 0


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
    [InlineKeyboardButton("Edit", callback_data="edit")],
    [InlineKeyboardButton("Pay", callback_data="pay")],
    [InlineKeyboardButton("Info", callback_data="info")],
    [InlineKeyboardButton("Help", callback_data="help")],
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
    is_user = check_user(user.id)
    if is_user is None and not user.is_bot:
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
    try:
        await update.message.reply_text(f"Edit your job types and websites here. If your job type is not listed here, select others, it will be included there. We are working on grouping jobs better and adding more websites. Feel free to send suggestions to roledropapp@gmail.com", reply_markup=get_user_category_keyboard(context.user_data.setdefault("categories", set())))
    except Forbidden:
        delete_user_by_id(user.id)
    except TimedOut:
        pass


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE, user_email: str = ""):
    """
    initialize paystack transaction
    """
    user = update.effective_user
    args = context.args
    query = update.callback_query
    no_email_text = "what is your email?\nyou can cancel payment by sending /cancel"

    if (verify_subscription(user.id)) == True:
        if (query):
            await query.answer()
            await update.effective_user.send_message("/pay")
        await context.bot.send_message(text="🤗 You're a paid user. Enjoy full access.", chat_id=update.effective_chat.id)

        return
    
    else:
        if args:
            email = context.args[0]
        elif user_email:
            email = user_email
        else:
            if query:
                await query.answer()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=no_email_text
                )
                return ASK_EMAIL
            else:
                await update.message.reply_text(no_email_text)
                return ASK_EMAIL
        
        paymentData = {
            "email": email,
            "amount": amount
        }

        pay_id = await make_payment(paymentData)
        pay_email = email
        pay_chat = update.effective_chat.id

        payKeyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Pay Now", url=f"{complete_payment}id={pay_id}&email={pay_email}&user={str(user.id)}&chat={str(pay_chat)}")]
        ])

        try:
            await update.message.reply_text(f"Click below to pay one thousand naira for 30 days FULL access 🤗\nREMEMBER: send /verify after payment to refresh", reply_markup=payKeyboard)
        except Forbidden:
            delete_user_by_id(user.id)

        return ConversationHandler.END

async def collect_email(update: Update, context:ContextTypes.DEFAULT_TYPE):
    """
    """
    email = update.message.text
    try:
        email_validator.validate_email(email)
    except:
        await update.message.reply_text(f"{email} is not a valid email. Please send /pay to enter a valid email. Thank you.")
        return ConversationHandler.END
    
    await update.message.reply_text(f"✅ got it {email}, thanks. now to payment...")
    await pay(update, context, email)
    
    return ConversationHandler.END

async def cancel(update: Update, cpntext:ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("🚫 payment cancelled. you can restart any time by sending /pay 'youremail'")
    except Forbidden:
        delete_user_by_id(update.effective_user.id)
    return ConversationHandler.END

async def timeout_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """
    """
    try:
        await update.effective_chat.send_message("⏰ Timeout. Didn't receive your email.\nYou can restart payment anytime by sending /pay email")
    except Forbidden:
        delete_user_by_id(update.effective_user.id)

    return ConversationHandler.END


async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, chatId: str = "", userId: str = ""):
    """
    """
    if chatId != "":
        chatId = chatId
    else:
        pass
    if userId != "":
        user = userId
    else:
        user = update.effective_user.id
    
    status = verify_subscription(user)
    if status == True:
        text = "🤗 You're a paid user. Enjoy full access."
    else:
        text = "😥 No paid access. Send /pay to subscribe for 30 days. 1k only."
    
    query = update.callback_query

    if query:
        await query.answer()
        await context.bot.send_message("/verify")
        await context.bot.send_message(text)
    else:
        await update.message.reply_text(text)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    """
    info = "👉 /edit to edit your job categories\n👉 /info to get information about your roledrop profile\n👉 /pay to pay 1,000 naira for 30 days access\n👉 send an email to roledropapp@gmail.com if you run into any problems"

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await update.effective_user.send_message(f"/help")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=info,
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(info, reply_markup=keyboard)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    """
    user = update.effective_user
    user_info = get_user_info(user.id)

    info = f"""*📢 {user.first_name.upper()}* \nSTATUS => {user_info["status"]} \nCATEGORIES => {user_info["categories"]} \nSITES => {user_info["sites"]} \n"""

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            await update.effective_user.send_message(f"/info")
            await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=info,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
            )
        except Forbidden:
            delete_user_by_id(user.id)
    else:
        try:
            await update.message.reply_markdown(info, reply_markup=keyboard)
        except Forbidden:
            delete_user_by_id(user.id)


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
    
    elif cmd == "pay":
        await pay(update, context)
    
    elif cmd == "verify":
        await verify_payment(update, context)
    
    elif cmd == "info":
        await info(update, context)
    
    elif cmd == "help":
        await help(update, context)


async def handle_invalid_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    """
    try:
        await update.message.reply_markdown("Invalid command 😥\n Try one of these", reply_markup=keyboard)
    except Forbidden:
        delete_user_by_id(update.effective_user.id)


def main_bot():
    """
    returns an instance of the roledrop bot
    """

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("pay", pay),
            CallbackQueryHandler(pay, "^pay$")
        ],
        states={
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_email)],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, timeout_handler)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        conversation_timeout=60,
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("edit", edit))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("verify", verify_payment))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_invalid_messages))

    return application

