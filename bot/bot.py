import random
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardButton, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _, activate, get_language

from bot.models import LoginCode

TOKEN = settings.BOT_TOKEN

dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_lang = message.from_user.language_code or 'uz'
    if user_lang not in ['uz', 'en', 'ru']:
        user_lang = 'uz'
    await sync_to_async(activate)(user_lang)

    code = random.randint(100000, 999999)
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=_('Nusxalash'),
            copy_text=CopyTextButton(text=f"{code}")
        )
    )

    await sync_to_async(LoginCode.objects.filter(chat_id=message.chat.id).delete)()

    await sync_to_async(LoginCode.objects.create)(
        chat_id=message.chat.id,
        code=str(code)
    )

    await message.answer(
        text=_("<b>Kirish kodi:</b>") + f" <code>{code}</code>\n\n" + _("<i>Kod faqat 1 daqiqa amal qiladi.</i>"),
        reply_markup=keyboard.as_markup()
    )


async def run_bot():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)