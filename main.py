import asyncio
import nest_asyncio
import uvicorn
from bot.tg_bot import main_bot
from db.db import init_db, get_all_users
from scrapers.linkedin import get_linkedin_jobs
import json
from deps.deps import parse_linkedin_jobs
from telegram.helpers import escape_markdown
from telegram.error import BadRequest


nest_asyncio.apply()


application = main_bot()

lj_world = ""
lj_ng = ""


async def run_linkedin():

    global lj_world, lj_ng
    # print("lj_world   ", lj_world)
    # print("lj_ng    ", lj_ng)

    while True:
        
        jobs = await asyncio.to_thread(get_linkedin_jobs)
        print("jobs     \n")
        # print(jobs)

        current_lj_world = jobs[0][0][-1] if (len(jobs[0]) > 0) else ""
        current_lj_ng = jobs[1][0][-1] if (len(jobs[1]) > 0) else ""

        # print("current_lj_world    ", current_lj_world)
        # print("current_lj_ng    ", current_lj_ng)

        grouped_jobs = parse_linkedin_jobs(jobs)
        
        users = get_all_users()
        for user in users:
            user_cats = json.loads(user[5])
            for cat in user_cats:
                available_jobs = grouped_jobs[cat]
                for job in available_jobs:
                    if job[-1] != current_lj_ng and job[-1] != current_lj_world:
                        job_desc = escape_markdown(job[3][:2000], version=2)
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
        lj_world = current_lj_world
        lj_ng = current_lj_ng
        # print("lj_world   ", lj_world)
        # print("lj_ng    ", lj_ng)

        current_lj_world = ""
        current_lj_ng = ""

        # print("current_lj_world    ", current_lj_world)
        # print("current_lj_ng    ", current_lj_ng)

        print("sleeping")
        jobs = []
        await asyncio.sleep(30)


async def main():
    config = uvicorn.Config(
        "server.server:app",
        host="127.0.0.1",
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
