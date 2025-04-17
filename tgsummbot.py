import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram import Router
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '7794147282:AAFhJFb2fTvVgQxzy20oehf7S0rV6hIF4dk'

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


@router.message()
async def handle_message(message: types.Message):
    text = message.text
    amounts = re.findall(r'-\s*([\d\s]+)₽', text)
    total = sum(int(a.replace(' ', '')) for a in amounts)
    await message.answer(f"<b>Общий баланс: {total}₽</b>")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
