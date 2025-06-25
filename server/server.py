from fastapi import FastAPI, Request, Response, BackgroundTasks
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
from telegram.error import BadRequest, TimedOut, Forbidden, RetryAfter
import aiosmtplib
from email.message import EmailMessage
import asyncio
import copy
from constants import categories_list

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
async def new_jobs(all_jobs: List[List[str]], background_tasks: BackgroundTasks):
    """
    """
    background_tasks.add_task(process_send_jobs, all_jobs)
    return HTTPStatus.OK 


async def process_send_jobs(all_jobs):
    """
    """
    grouped_jobs = parse_linkedin_jobs(all_jobs)
    job_mes = {}
    for item, value in grouped_jobs.items():
        job_str = f"""{item}\n\n"""
        for job in value:
            job_str += f"""💎💎  <b>{job[0]}</b>\n👉  {job[1]}\n📍  {job[2]}\n📍  {job[3]}\n\n"""
        job_str_chunks = split_by_diamond_start(job_str)
        job_mes[item] = job_str_chunks
    
    users = get_all_users()

    for user in users:
        user_cats = json.loads(user[5])
        for cat in user_cats:
            while True:
                try:
                    if len(job_mes[cat][0]) > 30:
                        for chunk in job_mes[cat]:
                            await application.bot.send_message(
                            chat_id=user[0],
                            text=chunk,
                            parse_mode="HTML"
                            )
                    break
                except BadRequest:
                    try:
                        await application.bot.send_message(
                        chat_id=user[0],
                        text=job_mes[cat][:4000]
                    )
                        break
                    except:
                        break
                except Forbidden:
                    delete_user_by_id(user[0])
                    break
                except RetryAfter as e:
                    retry_secs = int(e.retry_after)
                    print(f"flood control for {retry_secs}")
                    await asyncio.sleep(retry_secs + 2)
                except Exception as e:
                    print(f"unexpected error: {e}")
                    break
    await asyncio.sleep(0.5)


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


@app.post("/send_message/")
async def message_to_users(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    text = data["text"]
    background_tasks.add_task(message_users, text)


async def message_users(text):
    """
    """
    users = get_all_users()
    for user in users:
        try:
            application.bot.send_message(
                chat_id=user[0],
                text=text
            )
        except Forbidden:
            delete_user_by_id(user[0])
        except RetryAfter as e:
            retry_secs = e.retry_after
            print(f"flood control for {retry_secs} seconds")
            await asyncio.sleep(retry_secs + 2)
            pass
        except BadRequest:
            break
        except Exception as e:
            print(f"unexpected error: {e}")


@app.get("/expired/")
async def remind_unpaid_users():
    """
    """
    set_expired()
    ids = get_expired_users()
    for id in ids:
        try:
            await application.bot.send_message(
            chat_id=int(id[0]),
            text="Hi! \nA Your free trial has expired. \nWe just sent out 100+ newly posted jobs, which you can't see, unfortunately. \n👉 /pay to Pay one thousand naira today to get full access for 30 days. \nBe among the first to apply for jobs to get hired. \nFeel free to send us an email at roledropapp@gmail.com. \n1,000 for one month.  \nEnjoy 😉",
            reply_markup=keyboard
            )
        except Forbidden as e:
            delete_user_by_id(int(id[0]))
    ids = get_trial_users()
    for id in ids:
        try:
            await application.bot.send_message(
            chat_id=int(id[0]),
            text="""Hi! Hope you're enjoying Roledrop 🤗\nIn two days, your free trial will end. \nA gentle reminder to subscribe and keep getting the latest jobs to apply to. \nBe among the first to apply for jobs and get considered for interviews. \n1,000 for one month. Enjoy 😉""",
            reply_markup=keyboard
            )
        except Forbidden as e:
            delete_user_by_id(int(id[0]))

def split_by_diamond_start(text, base_limit=3900):
    chunks = []
    i = 0
    n = len(text)

    while i < n:
        # Tentative end
        end = min(i + base_limit, n)

        # Look ahead for the next 💎 after base limit
        diamond_pos = text.find("💎", end)

        if diamond_pos == -1:
            # No more 💎 ahead — take the rest
            chunks.append(text[i:])
            break

        # Ensure 💎 is the start of the next chunk
        chunks.append(text[i:diamond_pos])
        i = diamond_pos

    return chunks