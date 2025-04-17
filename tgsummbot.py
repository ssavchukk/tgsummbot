import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiohttp import web

TOKEN = "7794147282:AAFhJFb2fTvVgQxzy20oehf7S0rV6hIF4dk"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_message(message: Message):
    text = message.text
    total = 0
    for line in text.splitlines():
        if "₽" in line and "-" in line:
            try:
                part = line.split("-")[-1].replace("₽",
                                                   "").replace(" ", "").strip()
                total += int(part)
            except:
                pass
    await message.answer(f"💰 Общая сумма: {total}₽")


async def start_bot():
    await dp.start_polling(bot)


async def handle(request):
    return web.Response(text="Bot is running")


async def start_web():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()


async def main():
    await asyncio.gather(start_bot(), start_web())

if __name__ == "__main__":
    asyncio.run(main())
