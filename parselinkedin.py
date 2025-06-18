# from deps.deps import parse_linkedin_jobs
# from db.db import get_all_users
# import json
# from telegram.helpers import escape_markdown
# from server.server import application



# async def send_linkedin(jobs):
#     grouped_jobs = parse_linkedin_jobs(jobs)
    
#     users = get_all_users()
#     for user in users:
#         user_cats = json.loads(user[5])
#         for cat in user_cats:
#             available_jobs = grouped_jobs[cat]
#             for job in available_jobs:
#                 job_desc = escape_markdown("".join(job[3][:2000]).replace("\n\n", "\n"), version=2)
#                 try:
#                     await application.bot.send_message(chat_id=user[0],
#                                                     text=f"""[{cat}]\n*{job[0]}*\n{job[-1]}\n{job_desc}\n{job[1]}
#                                                         """,
#                                                     parse_mode="Markdown")
#                 except BadRequest as e:
#                     await application.bot.send_message(chat_id=user[0],
#                                                             text=f"""[{cat}]\n*{job[0]}*\n{job[-1]}\n{job[1]}
#                                                         """,
#                                                         parse_mode="Markdown")
#                 except TimedOut as e:
#                     print("telegram server timed out. moving on...")
