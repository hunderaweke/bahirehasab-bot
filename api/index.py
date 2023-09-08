import os
import hashlib
import asyncio
import logging
import postcard_drawer
from io import BytesIO
from bahire_hasab import BahireHasab
from fastapi import FastAPI
from PIL import Image, ImageDraw, ImageDraw2
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardButton,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    Message,
    InputMediaPhoto,
)
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware

TOKEN = os.environ.get("TOKEN")
WEBHOOK_HOST = "https://bc02-196-189-233-4.ngrok-free.app"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "localhost"
WEBAPP_PORT = 7000

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=["start", "help"])
async def start(msg: Message):
    keyboards = [
        [
            InlineKeyboardButton("📅 የዘመኑ ማውጫ", callback_data="calc_other"),
            InlineKeyboardButton("💡 እገዛ ላማግኘት", callback_data="help"),
        ],
        [
            InlineKeyboardButton("🇪🇹 የዘንድሮ ማውጫ", callback_data="this_year"),
            InlineKeyboardButton("✨  የሌላ ዓመት ማውጫ", callback_data="calc_other"),
        ],
        [InlineKeyboardButton("🥳 ፖስተ ካርድ ለመላከ", callback_data="post_card")],
    ]
    mark_up = InlineKeyboardMarkup(inline_keyboard=keyboards)
    await bot.send_message(
        chat_id=msg.chat.id,
        text=f"""
Welcome {msg.from_user.full_name} to ባህረ ሐሳብ 
This bot is made by Hundera Awoke © 

Follow me on:-
    github: @hunderaweke
    linkedin @hunderaweke
    telegram @hun_era

For more about the code of the bot visit:-
https://github.com/hunderaweke/bahirehasab-bot

Join my Telegram 💻 Channel:-
    @cod_nghub 
""",
    )
    await bot.send_message(
        chat_id=msg.chat.id,
        text="🖐 እንኳን ወደ ባህረ ሐሳብ 🗃️ መቀመሪያ በደህና መጡ",
        reply_markup=mark_up,
    )


@dp.callback_query_handler(text="this_year")
async def this_year(query: types.CallbackQuery):
    year = 2015
    await query.answer()
    bh = BahireHasab(year=year)
    await bot.send_message(chat_id=query.message.chat.id, text=f"{bh.erget}")


@dp.callback_query_handler(text="post_card")
async def post_card(query: types.CallbackQuery):
    await query.answer()
    template_1 = open("images/template-1.png", "rb")
    template_2 = open("images/template-2.png", "rb")
    keyboard = [
        [InlineKeyboardButton("☝ ይህን Template 🖼 ተጠቀም", callback_data="template_1")],
        [InlineKeyboardButton("☝ ይህን Template 🖼 ተጠቀም", callback_data="template_2")],
    ]
    await bot.send_photo(
        chat_id=query.message.chat.id,
        photo=template_1,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard[0]]),
    )
    await bot.send_photo(
        chat_id=query.message.chat.id,
        photo=template_2,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard[1]]),
    )


@dp.callback_query_handler(text="template_1")
@dp.callback_query_handler(text="template_2")
async def send_post_card(query: types.CallbackQuery):
    await query.answer("Sending the picture")
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    if query.data == "template_1":
        selected_template = "images/template-1.png"
    else:
        selected_template = "images/template-2.png"
    sender_name = query.from_user.full_name
    receiver_name = ""
    await bot.send_message(
        chat_id=query.from_user.id,
        text=f"💁 Send the sender's name please or press /skip \n የሚልከውን ስም ያስገቡ \n Default: {sender_name}",
    )
    STATES = {"SENDER_NAME_STATE": 1, "RECEIVER_NAME_STATE": 2}
    current_state = STATES["SENDER_NAME_STATE"]

    @dp.message_handler()
    async def handle_names(message: Message):
        nonlocal sender_name, receiver_name, current_state
        if current_state == STATES["SENDER_NAME_STATE"]:
            if message.text != "/skip":
                sender_name = message.text
            await bot.send_message(
                chat_id=query.from_user.id,
                text=f"💁 Send the Recevier's name please or press.\n ✉ የሚላክለትን ሰው ስም ያስገቡ፡ ",
            )
        elif current_state == STATES["RECEIVER_NAME_STATE"]:
            receiver_name = message.text

    img = postcard_drawer.draw_post_card(
        sender_name=sender_name,
        reciever_name=receiver_name,
        template_name=selected_template,
    )
    await bot.send_photo(chat_id=query.from_user.id, photo=img)
    return


@dp.inline_handler()
async def this_year_inline(query: InlineQuery):
    year = int(query.query) or 2015
    bh = BahireHasab(year=year)
    input_content = InputTextMessageContent(f"{bh.erget}")
    result_id: str = hashlib.md5(str(year).encode()).hexdigest()
    result_id2: str = hashlib.md5(str(year + 1).encode()).hexdigest()
    items = [
        InlineQueryResultArticle(
            id=result_id, title="እርገት", input_message_content=input_content
        ),
        InlineQueryResultArticle(
            id=result_id2,
            title="ትንሳኤ",
            input_message_content=InputTextMessageContent(f"{bh.tnsae}"),
        ),
    ]
    await bot.answer_inline_query(query.id, results=items, cache_time=1)


async def on_startup(dp: Dispatcher):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp: Dispatcher):
    logging.warning("Shutting down ....")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Good bye!")


# asyncio.run(
#     start_webhook(
#         dispatcher=dp,
#         webhook_path=WEBHOOK_PATH,
#         on_startup=on_startup,
#         on_shutdown=on_shutdown,
#         skip_updates=True,
#         host=WEBAPP_HOST,
#         port=WEBAPP_PORT,
#     )
# )

asyncio.run(dp.start_polling(fast=True))
