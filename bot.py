from db import add_order, update_status as db_update_status, add_order_update
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from uuid import uuid4

# === Настройки ===
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не найден! Проверь .env файл")
print("DEBUG | BOT_TOKEN:", os.getenv("BOT_TOKEN"))
print("DEBUG | GROUP_ID:", os.getenv("GROUP_ID"))
print("DEBUG | DATABASE_URL:", DATABASE_URL)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

LANGS = {
    'ru': {
        'welcome': "🔧 Добро пожаловать! Введите ваше <b>имя</b>:",
        'phone': "📞 Введите телефон:",
        'address': "🏠 Введите адрес:",
        'description': "🛠 Опишите работу:",
        'media': "📷 Отправьте фото или видео, или напишите <i>пропустить</i>",
        'sent': "✅ Заявка отправлена!",
        'error': "⚠ Отправьте фото, видео или 'пропустить'",
        'confirm': "✅ Заявка принята!",
        'contact': "Мы свяжемся с вами в ближайшее время!"
    },
    'en': {
        'welcome': "🔧 Welcome! Please enter your <b>name</b>:",
        'phone': "📞 Enter your phone number:",
        'address': "🏠 Enter your address:",
        'description': "🛠 Describe the job:",
        'media': "📷 Send a photo or video, or type <i>skip</i>",
        'sent': "✅ Request submitted!",
        'error': "⚠ Send a photo, video, or 'skip'",
        'confirm': "✅ Request submitted!",
        'contact': "We will contact you shortly!"
    }
}

request_counters = {}

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Хранилище временных заявок ===
user_states = {}
media_groups = {}

# === Кнопки статуса ===
def status_buttons(req_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 В процессе", callback_data=f"in_progress:{req_id}")],
        [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done:{req_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{req_id}")]
    ])

# === Формирование текста заявки ===
def render_request(data: dict):
    now = datetime.now()
    created_at = now.strftime("%m/%d/%Y %I:%M %p")
    date_key = now.strftime("%m%d%Y")
    request_counters.setdefault(date_key, 0)
    request_counters[date_key] += 1
    req_number = f"#REQ-{date_key}-{request_counters[date_key]:03d}"
    data['req_number'] = req_number
    return (
        f"<b>Новая заявка!</b>\n"
        f"🧾 Номер: {data['req_number']}\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"🏠 Адрес: {data['address']}\n"
        f"📝 Описание: {data['description']}\n"
        f"📌 Статус: <b>{data['status']}</b>\n"
        f"⏰ Время: {created_at}"
    )

# === Обновление статуса ===
def update_status_text(text: str, new_status: str) -> str:
    lines = [line for line in text.splitlines() if not line.strip().startswith("Новая заявка!")]
    for i, line in enumerate(lines):
        if line.startswith("📌 Статус:"):
            lines[i] = f"📌 Статус: <b>{new_status}</b>"
            break
    return "\n".join(lines)

# === Команда /start ===
@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")]
    ])
    await message.answer_photo(
        photo="https://telegra.ph/file/9361C60E6BC640579CC160.png",  # твой логотип
        caption="Добро пожаловать в <b>Chicago Handyman Services</b>! 👷‍♂️🔧",
        parse_mode=ParseMode.HTML
    )
    await message.answer("🌐 Выберите язык / Choose your language:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("lang:"))
async def choose_lang(call: types.CallbackQuery):
    lang = call.data.split(":")[1]
    user_states[call.from_user.id] = {"step": "name", "lang": lang}
    await call.message.answer(LANGS[lang]["welcome"])
    await call.answer()

# === Заполнение заявки ===
@dp.message(F.chat.type == "private")
async def collect(message: types.Message):
    state = user_states.get(message.from_user.id)
    if not state:
        return await message.answer("Введите /start для начала")

    lang = state.get("lang", "ru")
    step = state["step"]
    text = message.text

    if step == "name":
        state["name"] = text
        state["step"] = "phone"
        await message.answer(LANGS[lang]["phone"])

    elif step == "phone":
        state["phone"] = text
        state["step"] = "address"
        await message.answer(LANGS[lang]["address"])

    elif step == "address":
        state["address"] = text
        state["step"] = "description"
        await message.answer(LANGS[lang]["description"])

    elif step == "description":
        state["description"] = text
        state["step"] = "media"
        await message.answer(LANGS[lang]["media"])

    elif step == "media":
        media = []
        if message.media_group_id:
            media_groups.setdefault(message.media_group_id, []).append(message)
            await asyncio.sleep(2)
            messages = media_groups.pop(message.media_group_id)
            if message != messages[-1]:
                return

            for msg in messages:
                if msg.photo:
                    media.append(InputMediaPhoto(media=msg.photo[-1].file_id))
                elif msg.video:
                    media.append(InputMediaVideo(media=msg.video.file_id))

        elif message.photo:
            media.append(InputMediaPhoto(media=message.photo[-1].file_id))
        elif message.video:
            media.append(InputMediaVideo(media=message.video.file_id))
        elif text and text.lower() == "пропустить":
            pass
        else:
            return await message.answer(LANGS[lang]["error"])

        req_id = str(uuid4())
        state["req_id"] = req_id
        add_order(state)
        state["status"] = "новая"
        caption = render_request(state)

        try:
            if media:
                message_group = await bot.send_media_group(GROUP_ID, media)
                media_message_ids = [msg.message_id for msg in message_group]
                state["media_message_ids"] = media_message_ids
                user_states[req_id] = dict(state)
                await bot.send_message(
                    GROUP_ID,
                    caption,
                    reply_markup=status_buttons(req_id),
                    reply_to_message_id=message_group[-1].message_id
                )
            else:
                await bot.send_message(GROUP_ID, caption, reply_markup=status_buttons(req_id))
            await message.answer(f"{LANGS[lang]['confirm']}\n🧾 Номер: {state['req_number']}\n📞 {LANGS[lang]['contact']}")
            await message.answer(LANGS[lang]["sent"])
        except Exception as e:
            await message.answer(f"❌ Ошибка при отправке:\n<code>{e}</code>", parse_mode="HTML")
            logging.exception(e)

        user_states.pop(message.from_user.id, None)

# === Обработка кнопок ===
@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    try:
        logging.info(f"Получен callback: {call.data}")
        if ":" not in call.data or not call.message:
            await call.answer("Неверный формат или сообщение не найдено")
            return

        action, req_id = call.data.split(":")
        msg = call.message
        text = msg.caption or msg.text or ""
        new_status = {
            "in_progress": "в процессе",
            "done": "выполнено",
            "delete": "удалено"
        }.get(action)

        if not new_status:
            return await call.answer("Неизвестное действие")

        if action == "delete":
            # Удаляем все медиа-сообщения, если они есть
            user_data = user_states.get(req_id)
            if user_data and "media_message_ids" in user_data:
                for media_id in user_data["media_message_ids"]:
                    try:
                        await bot.delete_message(msg.chat.id, media_id)
                    except Exception as e:
                        logging.warning(f"Ошибка удаления медиа {media_id}: {e}")

            await msg.delete()
            return await call.answer("Удалено")

        new_text = update_status_text(text, new_status)

        if not new_text or new_text.strip() == text.strip():
            await call.answer("Статус уже установлен")
            return

        try:
            if msg.caption:
                await bot.edit_message_caption(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=new_text,
                    reply_markup=status_buttons(req_id)
                )
            else:
                await bot.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=new_text,
                    reply_markup=status_buttons(req_id)
                )
            db_update_status(req_id, str(new_status))
            add_order_update(order_id=req_id, update_type=str(new_status))
            await call.answer("Статус обновлён")
        except Exception as e:
            logging.exception(e)
            await call.answer("Ошибка при редактировании сообщения")
    except Exception as e:
        logging.exception(e)
        await call.answer("Ошибка обработки")

# === Запуск ===
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
