from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from telegram.ext import Application
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from deps.deps import parse_linkedin_jobs, format_text_as_html
from db.db import get_all_users, delete_user_by_id, count_users, complete_payment, set_expired, get_expired_users, get_trial_users
import json
from telegram.helpers import escape_markdown
from telegram.error import BadRequest, TimedOut, Forbidden
import aiosmtplib
from email.message import EmailMessage
import asyncio

load_dotenv(override=True)
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
EMAIL = os.getenv("EMAIL")


commands = [
    BotCommand("edit", "Edit your job categories"),
    BotCommand("info", "Show your info"),
    BotCommand("help", "Get help"),
    BotCommand("pay", "Pay for one month (30 days)"),
    BotCommand("verify", "Verify payment")
]

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Pay", callback_data="pay")],
    [InlineKeyboardButton("Edit", callback_data="edit")],
    [InlineKeyboardButton("Info", callback_data="info")],
    [InlineKeyboardButton("Help", callback_data="help")],
])

application = (
    Application
        .builder()
        .updater(None)
        .token(BOT_TOKEN)
        .read_timeout(60)
        .get_updates_read_timeout(60)
        .build()
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    to run each time server starts and stops
    """
    await application.bot.set_my_commands(commands)

    await application.bot.set_webhook(
        WEBHOOK_URL,
        drop_pending_updates=True,
        connect_timeout=30,
        pool_timeout=30,
        read_timeout=30,
        write_timeout=30
    )

    await application.initialize()

    yield

    print("shutting down")
    # await application.stop()
    await send_email()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    """
    sanity check
    """
    return {
        "status": "OK"
    }

@app.post("/telegram/webhook/")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return Response(status_code=HTTPStatus.OK)

@app.get("/count/")
async def user_count():
    total_count, status_count = count_users()
    count_dict = {"total": total_count}
    count_dict.update(status_count)
    
    return count_dict


@app.post("/send_linkedin_jobs/")
async def new_jobs(all_jobs: List[List[str]]):
    """
    """
    grouped_jobs = parse_linkedin_jobs(all_jobs)
    
    users = get_all_users()
    for user in users:
        user_cats = json.loads(user[5])
        for cat in user_cats:
            available_jobs = grouped_jobs[cat]
            for job in available_jobs:
                job_desc = format_text_as_html("".join(job[5][:3000]).replace("\n", "\n"))
                try:
                    await application.bot.send_message(chat_id=user[0],
                                                    text=f"""{cat}\n💎💎  <b>{job[0]}</b>\n👉  {job[-1]}\n📍  {job[2]}\n{job[3]}\n{job[4]}\n{job_desc}\n👉  {job[1]}\n
                                                        """, parse_mode="HTML")
                except BadRequest:
                    await application.bot.send_message(chat_id=user[0],
                                                            text=f"""[{cat}]\n*{job[0]}*\n{job[-1]}\n{job[1]}
                                                        """,
                                                        parse_mode="Markdown")
                except TimedOut:
                    print("telegram server timed out. moving on...")
                except Forbidden:
                    delete_user_by_id(user[0])
                await asyncio.sleep(1)


async def send_email():
    """
    send db to email
    """
    EMAIL_ADDRESS = EMAIL
    EMAIL_PASSWORD = APP_PASSWORD

    message = EmailMessage()
    message["From"] = EMAIL_ADDRESS
    message["To"] = EMAIL_ADDRESS
    message["Subject"] = "Roledrop shutdown, backup"

    message.set_content("Roledrop shutdown successfully. Here's the backup, engineer NG.")

    db = "rd_users.db"
    with open(db, "rb") as f:
        message.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename="rd_users.db")

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=EMAIL_ADDRESS,
        password=EMAIL_PASSWORD
    )


@app.post("/complete_payment/")
async def complete_payment_be(request: Request):
    data = await request.json()
    id = int(data["id"])
    reference = data["reference"]
    complete_payment(id, reference)
    return {
        "status": "ok"
    }


@app.get("/expired/")
async def remind_unpaid_users():
    """
    """
    set_expired()
    ids = get_expired_users()
    for id in ids:
        await application.bot.send_message(
            chat_id=int(id[0]),
            text="Hi! \nA gentle reminder to subscribe and keep getting the latest jobs to apply to. \nBe among the first to apply for jobs and get considered for interviews. \n1,000 for one month. Enjoy 😉",
            reply_markup=keyboard
        )
    ids = get_trial_users()
    for id in ids:
        await application.bot.send_message(
            chat_id=int(id[0]),
            text="""Hi! Hope you're enjoying Roledrop 🤗\nIn a few days, your free trial will end. \nA gentle reminder to subscribe and keep getting the latest jobs to apply to. \nBe among the first to apply for jobs and get considered for interviews. \n1,000 for one month. Enjoy 😉""",
            reply_markup=keyboard
        )

