from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from telegram.ext import Application
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus
from telegram import Update
from typing import List
from deps.deps import parse_linkedin_jobs
from db.db import get_all_users
import json
from telegram.helpers import escape_markdown
from telegram.error import BadRequest, TimedOut

load_dotenv(override=True)
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

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

    await application.stop()


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

@app.post("/send_linkedin_jobs")
async def new_jobs(all_jobs: List[dict]):
    """
    """
    grouped_jobs = parse_linkedin_jobs(all_jobs)
    
    users = get_all_users()
    for user in users:
        user_cats = json.loads(user[5])
        for cat in user_cats:
            available_jobs = grouped_jobs[cat]
            for job in available_jobs:
                job_desc = escape_markdown("".join(job[3][:2000]).replace("\n\n", "\n"), version=2)
                try:
                    await application.bot.send_message(chat_id=user[0],
                                                    text=f"""[{cat}]\n*{job[0]}*\n{job[-1]}\n{job_desc}\n{job[1]}
                                                        """,
                                                    parse_mode="Markdown")
                except BadRequest as e:
                    await application.bot.send_message(chat_id=user[0],
                                                            text=f"""[{cat}]\n*{job[0]}*\n{job[-1]}\n{job[1]}
                                                        """,
                                                        parse_mode="Markdown")
                except TimedOut as e:
                    print("telegram server timed out. moving on...")

