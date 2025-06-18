import asyncio
import nest_asyncio
import uvicorn
from bot.tg_bot import main_bot
from db.db import init_db, get_all_users
import json
from deps.deps import parse_linkedin_jobs
from telegram.helpers import escape_markdown
from telegram.error import BadRequest, TimedOut
from dotenv import load_dotenv
import os


nest_asyncio.apply()

load_dotenv(override=True)
LI_AT = os.getenv("LI_AT_COOKIE")


application = main_bot()

async def main():
    config = uvicorn.Config(
        "server.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
        )
    server = uvicorn.Server(config)

    server_run = asyncio.create_task(server.serve())

    await asyncio.gather(server_run)

if __name__=="__main__":
    init_db()
    asyncio.run(main())
