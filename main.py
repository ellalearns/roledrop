import asyncio
import nest_asyncio
import uvicorn
from bot.tg_bot import main_bot
from db.db import init_db, get_all_users
from scrapers.linkedin import get_linkedin_jobs
import json
from deps.deps import parse_linkedin_jobs, return_unseen_jobs
from telegram.helpers import escape_markdown
from telegram.error import BadRequest, TimedOut


nest_asyncio.apply()


application = main_bot()

lj_world = ""
lj_ng = ""


async def run_linkedin():

    global lj_world, lj_ng

    while True:
        
        jobs = await asyncio.to_thread(get_linkedin_jobs)

        current_lj_world = jobs[0][0][-1] if (len(jobs[0]) > 0) else lj_world
        current_lj_ng = jobs[1][0][-1] if (len(jobs[1]) > 0) else lj_ng

        unseen_jobs = return_unseen_jobs(jobs, lj_world, lj_ng)
        
        grouped_jobs = parse_linkedin_jobs(unseen_jobs)
        
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
        lj_world = current_lj_world
        lj_ng = current_lj_ng

        current_lj_world = ""
        current_lj_ng = ""

        print("sleeping")
        jobs = []
        await asyncio.sleep(300)


async def main():
    config = uvicorn.Config(
        "server.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
        )
    server = uvicorn.Server(config)

    server_run = asyncio.create_task(server.serve())
    linkedin = asyncio.create_task(run_linkedin())

    await asyncio.gather(server_run, linkedin)

if __name__=="__main__":
    init_db()
    asyncio.run(main())
