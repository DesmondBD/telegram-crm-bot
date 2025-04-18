from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
import asyncio

TOKEN = '7909440129:AAEBPXGVANRl5eCOfI2U42vPrnlNZsBfjVQ'  # <-- замени на свой токен!

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message()
async def get_group_id(message: Message):
    await message.answer(f"<b>Group ID:</b> <code>{message.chat.id}</code>")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())