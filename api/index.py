import os
import hashlib
import asyncio
import logging
import postcard_drawer
from bahire_hasab import BahireHasab
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    Message,
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
storage = MemoryStorage()
store = {}
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level=logging.INFO)


class SenderReceiverStates(StatesGroup):
    SENDER_NAME = State()
    RECEIVER_NAME = State()
    SEND_IMAGE = State()


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
async def send_post_card(query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    keyboard = [
        [
            InlineKeyboardButton("ስም ለማስገባት", callback_data="sender-name"),
        ],
    ]
    selected_template = "images/template-1.png"
    if query.data == "template_1":
        selected_template = "images/template-1.png"
    else:
        selected_template = "images/template-2.png"
    store["selected_template"] = selected_template
    await bot.send_message(
        chat_id=query.from_user.id,
        text=f"💁 Send the sender's and receiver's name please or press /skip \n የሚልከውን እና የተቀባይ ሰው ስም ያስገቡ \n Default(የላኪው): {query.from_user.full_name}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await state.update_data(selected_template=selected_template)
    await state.update_data(current_state="SENDER_NAME_STATE")


@dp.callback_query_handler(text="sender-name")
async def sender_name_handler(query: types.CallbackQuery):
    await query.answer()
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=query.from_user.id, text="Send the sender's name 🤞\n የሚለክው ሰው ስም፡ "
    )
    await SenderReceiverStates.SENDER_NAME.set()


@dp.message_handler(state=SenderReceiverStates.SENDER_NAME)
async def get_sender_name(message: Message):
    sender_name = message.from_user.full_name
    sender_name = message.text
    store["sender_name"] = sender_name
    await SenderReceiverStates.RECEIVER_NAME.set()
    await bot.send_message(
        chat_id=message.chat.id, text="Send the receiver's name 🎁 \n የተቀባይ ሰው ስም፡ "
    )


@dp.message_handler(state=SenderReceiverStates.RECEIVER_NAME)
async def get_receiver_name(message: Message):
    receiver_name = message.text
    store["receiver_name"] = receiver_name
    await SenderReceiverStates.SEND_IMAGE.set()
    keyboard = [
        [
            InlineKeyboardButton("Send Image", callback_data="send-post-card"),
            InlineKeyboardButton("Cancel", callback_data="cancel"),
        ]
    ]
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"የሚላክለት ሰው ስም:👉 {receiver_name}📭 \n የሚልከው ሰው ስም:👉 {store['sender_name']} 😎",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )



@dp.callback_query_handler(text="cancel", state=SenderReceiverStates.SEND_IMAGE)
async def cancel(query: types.CallbackQuery, state: FSMContext):
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
    await query.answer("Canceled Successfully!")
    await bot.delete_message(
        chat_id=query.from_user.id, message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=query.from_user.id,text="😇 ዳግም ለመሞከር 🥳  ፡  ",reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboards)
    )
    await state.finish()


@dp.callback_query_handler(text="send-post-card", state=SenderReceiverStates.SEND_IMAGE)
async def send_image(query: types.CallbackQuery, state: FSMContext):
    receiver_name = store["receiver_name"]
    sender_name = store["sender_name"]
    selected_template = store["selected_template"]
    img = postcard_drawer.draw_post_card(
        sender_name=sender_name,
        reciever_name=receiver_name,
        template_name=selected_template,
    )
    await bot.send_chat_action(
        chat_id=query.from_user.id, action=types.ChatActions.UPLOAD_PHOTO
    )
    await bot.send_photo(chat_id=query.from_user.id, photo=img)
    await state.finish()


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
