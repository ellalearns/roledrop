from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from telegram.ext import Application
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus
from telegram import Update


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
