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

async def send_linkedin(jobs):
    grouped_jobs = parse_linkedin_jobs(jobs)
    
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
