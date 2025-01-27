import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import TELEGRAM_TOKEN

from Database.database import db
from Source.handlers import router

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot, db = db)

# async def main():
#     dp.include_router(router)
#     await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print ('Bot stopped!')