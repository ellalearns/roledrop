import asyncio
import nest_asyncio
import uvicorn
from bot.tg_bot import main_bot
from db.db import init_db


nest_asyncio.apply()


application = main_bot()


async def main():
    config = uvicorn.Config(
        "server.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
        )
    server = uvicorn.Server(config)

    server_run = asyncio.create_task(server.serve())

    await server_run


if __name__=="__main__":
    init_db()
    asyncio.run(main())
