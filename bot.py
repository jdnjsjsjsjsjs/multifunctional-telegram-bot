from sys import path_hooks
from tkinter import image_types

from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.enums.chat_action import ChatAction
from pathlib import Path
import asyncio

from telebot.types import CallbackQuery

import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
BOT_USERNAME = os.getenv("BOT_USERNAME")
SHEET_LINK = os.getenv("SHEET_LINK")
DESIGN_LESSONS_LINK = os.getenv("DESIGN_LESSONS_LINK")
EDITING_LESSONS_LINK = os.getenv("EDITING_LESSONS_LINK")
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME")
EMAIL = os.getenv("EMAIL")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PORTFOLIO_LINK = os.getenv("PORTFOLIO_LINK")

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()

last_voice_ids = {}

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❓ Почему мы?"), KeyboardButton(text="🖼 ВИТРИНА")],
        [KeyboardButton(text="🤖 REELS BOT"), KeyboardButton(text="💬 Получить консультацию")],
        [KeyboardButton(text="🆓 Бесплатные продукты"), KeyboardButton(text="🔗 Реферальный центр")],
        [KeyboardButton(text="👀 О нас"), KeyboardButton(text="💳 Быстрый заказ")]
    ],
    resize_keyboard=True
)

async def send_voice_message(chat_id: int, voice_file: FSInputFile, caption: str, buttons: list[list[InlineKeyboardButton]]) -> types.Message:
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VOICE)
    return await bot.send_voice(
        chat_id=chat_id,
        voice=voice_file,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode=ParseMode.HTML
    )

@router.message(CommandStart())
async def start_handler(message: Message):
    video_path = BASE_DIR / "media" / "studio_circle.mp4"
    video = FSInputFile(video_path)
    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO_NOTE)
    await message.answer_video_note(video)

    image_path = BASE_DIR / "media" / "studio_card.jpg"
    image = FSInputFile(image_path)
    await message.answer_photo(
        photo=image,
        caption="🎬 <b>Добро пожаловать в КОТИКОВ</b> — контент-студию полного цикла, где каждый проект — это не просто красивая картинка, а инструмент влияния на аудиторию.\n\n"
                "🧠 Сейчас побеждает не дизайн, не видео, не звук — а идея, превращённая в цепляющий контент. Мы умеем делать это системно, точно и с характером.\n\n"
                "<b>В нашей команде:</b>\n"
                "🎞 Монтажёры, собирающие видеоряд с нервом и качом\n"
                "🎨 Дизайнеры, которые видят визуал, как архитекторы\n"
                "👾 Программисты, что оживляют интерфейсы и чат-ботов\n"
                "🖍 Иллюстраторы, передающие смыслы через рисунок\n"
                "📱 Контент-режиссёры, превращающие хаос в сериал\n\n"
                "💥 Мы строим не просто ролики и посты. Мы создаём реальность, которую зритель хочет пересматривать и расшаривать друзьям.\n\n"
                "📩 Пиши, если хочешь, чтобы про тебя не просто узнали — а чтобы запомнили."
    )

    user_status = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=message.from_user.id)

    if user_status.status in ["member", "administrator", "creator"]:
        await message.answer("✅ Вы подписаны!", reply_markup=main_menu)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton(text="🔄 Я подписался", callback_data="check_sub")]
        ])
        await message.answer(
            "❌ Вы не подписаны на канал!\n\nПожалуйста, подпишитесь и нажмите кнопку ниже 👇",
            reply_markup=kb
        )

@router.callback_query(F.data == "check_sub")
async def check_sub(query: types.CallbackQuery):
    user_status = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=query.from_user.id)

    if user_status.status in ["member", "administrator", "creator"]:
        await query.message.edit_text("✅ Спасибо за подписку!")
        await query.message.answer("Вот ваше меню:", reply_markup=main_menu)
    else:
        await query.answer("❌ Вы всё ещё не подписаны!", show_alert=True)

@router.message(F.text == "❓ Почему мы?")
async def why_us_handler(message: Message):
    voice_path = BASE_DIR / "media" / "why_us.ogg"
    if not voice_path.exists():
        await message.answer("⚠️ Голосовое сообщение не найдено.")
        return

    voice = FSInputFile(voice_path)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я не верю, что это поможет...", callback_data="no_believe")],
        [InlineKeyboardButton(text="Для чего мне это?", callback_data="why_me")],
        [InlineKeyboardButton(text="Вы инфоцыгане!", callback_data="info_business")],
        [InlineKeyboardButton(text="Я всё понял!", callback_data="understood")]
    ])

    sent = await send_voice_message(
        chat_id=message.chat.id,
        voice_file=voice,
        caption="🎙 <b>Чем мы занимаемся?</b>",
        buttons=kb.inline_keyboard
    )

    last_voice_ids[message.chat.id] = sent.message_id

@router.callback_query(F.data == "why_us")
async def why_us_link(callback: types.CallbackQuery):
    voice_path = BASE_DIR / "media" / "why_us.ogg"
    if not voice_path.exists():
        await callback.message.answer("⚠️ Голосовое сообщение не найдено.")
        await callback.answer()
        return
    voice = FSInputFile(voice_path)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я не верю, что это поможет...", callback_data="no_believe")],
        [InlineKeyboardButton(text="Для чего мне это?", callback_data="why_me")],
        [InlineKeyboardButton(text="Вы инфоцыгане!", callback_data="info_business")],
        [InlineKeyboardButton(text="✅ Я всё понял!", callback_data="understood")]
    ])
    chat_id = callback.message.chat.id
    try:
        await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
    except Exception:
        pass
    sent = await send_voice_message(
        chat_id=chat_id,
        voice_file=voice,
        caption="<b>Чем мы занимаемся?</b>",
        buttons=kb.inline_keyboard
    )
    last_voice_ids[chat_id] = sent.message_id
    await callback.answer()


async def handle_voice_with_back(query: types.CallbackQuery, file_name: str, caption: str):
    chat_id = query.message.chat.id
    if chat_id in last_voice_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_voice_ids[chat_id])
        except:
            pass
    voice_path = BASE_DIR / "media" / file_name
    if not voice_path.exists():
        await query.message.answer("⚠️ Голосовое сообщение не найдено.")
        return
    voice = FSInputFile(voice_path)
    back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_why_us")]
    ])

    sent = await send_voice_message(
        chat_id=chat_id,
        voice_file=voice,
        caption=caption,
        buttons=back_button.inline_keyboard
    )

    last_voice_ids[chat_id] = sent.message_id
    await query.answer()

@router.callback_query(F.data == "no_believe")
async def no_believe_callback(query: types.CallbackQuery):
    await handle_voice_with_back(
        query=query,
        file_name="no_believe.ogg",
        caption="😎 Ну, скепсис — это нормально. Мы покажем кейсы, которые говорят сами за себя."
    )

@router.callback_query(F.data == "why_me")
async def why_me_callback(query: types.CallbackQuery):
    await handle_voice_with_back(
        query=query,
        file_name="why_me.ogg",
        caption="🚀 Потому что ты не просто пользователь, а создатель. Контент — это сила, и мы даём тебе инструменты."
    )

@router.callback_query(F.data == "info_business")
async def info_business_callback(query: types.CallbackQuery):
    await handle_voice_with_back(
        query=query,
        file_name="info_business.ogg",
        caption="👆 Поговорим о подозрениях в инфоцыганстве"
    )

@router.callback_query(F.data == "understood")
async def understood_callback(query: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")
    image_path = BASE_DIR / "media" / "thank_you.jpg"
    image = FSInputFile(image_path)
    menu_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Сделать свой контент круче!", callback_data="go_main_menu")]
    ])
    await query.message.answer_photo(
        photo=image,
        caption="🔥 Бро, ты красавчик! Важно лишь преодолеть свои страхи и полететь дальше!\n"
                "Давай работать вместе в таком случае. Если что-то будет непонятно - можешь написать нашему менеджеру!",
        reply_markup=menu_button
    )
    await query.answer()

@router.callback_query(F.data == "back_to_why_us")
async def back_to_why_us(query: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")
    await why_us_handler(query.message)
    await query.answer()

@router.callback_query(F.data == "go_main_menu")
async def go_main_menu_callback(query: types.CallbackQuery):
    await query.message.answer("📋 Главное меню:", reply_markup=main_menu)
    await query.answer()

@router.message(F.text == "🤖 REELS BOT")
async def neuro_bot(message: Message):
    image_path = BASE_DIR / "media" / "bot_image.jpg"
    if not image_path.exists():
        await message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "🤖 <b>НЕЙРОКОТ</b> - это бот, который спасёт всех создателей контента!\n"
        "📲 Он преобразовывает любое видео в сценарий для ролика, который можно потом использовать в своём креативе!\n\n"
        "👇 Нажми кнопку ниже и увидишь ещё кое-что о нашей инновации!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить доступ к боту", callback_data="get_access_to_bot")]
    ])
    await message.answer_photo(
        photo=image,
        caption=caption,
        reply_markup=kb
    )

@router.callback_query(F.data == "reels_bot")
async def neuro_bot_about_us(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "bot_image.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "🤖 <b>НЕЙРОКОТ</b> - это бот, который спасёт всех создателей контента!\n"
        "📲 Он преобразовывает любое видео в сценарий для ролика, который можно потом использовать в своём креативе!\n\n"
        "👇 Нажми кнопку ниже и увидишь ещё кое-что о нашей инновации!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить доступ к боту", callback_data="get_access_to_bot")]
    ])
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image,
        caption=caption,
        reply_markup=kb
    )

@router.callback_query(F.data == "get_access_to_bot")
async def neuro_bot_access(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "bot_image_access.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "🖼 Если ты креатор контента и ты не уверен, что стоит пробовать воспользоваться нашим клёвым ботом, то...\n\n"
        "Вот тебе примеры работы нашего инструмента на картинках выше!\n"
        "👇 Не сомневайся - заходи и пробуй по кнопке, тебе доступно 3 бесплатных генерации!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Опробовать бота!", url=f"https://t.me/{BOT_USERNAME[1:]}")]
    ])
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image,
        caption=caption,
        reply_markup=kb
    )

@router.message(F.text == "🆓 Бесплатные продукты")
async def free_products(message: Message):
    image_path = BASE_DIR / "media" / "free_products.jpg"
    if not image_path.exists():
        await message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "🎁 Йоу, хочешь получить наши бесплатные продукты? Тогда выбирай из списка ниже!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить REELS BOT", callback_data="reels_bot")],
        [InlineKeyboardButton(text="Получить Таблицу продуктивности", callback_data="productivity_sheet")],
        [InlineKeyboardButton(text="Получить 5 уроков дизайна", callback_data="design_lessons")],
        [InlineKeyboardButton(text="Получить 5 уроков по монтажу", callback_data="editing_lessons")],
        [InlineKeyboardButton(text="Получить консультацию по дизайну", callback_data="design_consult")]
    ])
    await message.answer_photo(
        photo=image,
        caption=caption,
        reply_markup=kb
    )

@router.callback_query(F.data == "back_to_free_products")
async def back_to_free_products(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "free_products.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "🎁 Йоу, хочешь получить наши бесплатные продукты? Тогда выбирай из списка ниже!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить REELS BOT", callback_data="reels_bot")],
        [InlineKeyboardButton(text="Получить Таблицу продуктивности", callback_data="productivity_sheet")],
        [InlineKeyboardButton(text="Получить 5 уроков дизайна", callback_data="design_lessons")],
        [InlineKeyboardButton(text="Получить 5 уроков по монтажу", callback_data="editing_lessons")],
        [InlineKeyboardButton(text="Получить консультацию по дизайну", callback_data="design_consult")]
    ])
    await callback.message.edit_media(
        media=InputMediaPhoto(media=image, caption=caption),
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "productivity_sheet")
async def productivity_sheet(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "sheet.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "🌐 Эта таблица поможет тебе сделать так, чтобы твои дела оставались в порядке, а продуктивность не страдала!\n\n"
        "👇 Забирай её по кнопке ниже и пользуйся на здоровье!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Забрать таблицу", url=f"{SHEET_LINK}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_free_products")]
    ])
    await callback.message.edit_media(
        media=InputMediaPhoto(media=image, caption=caption),
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "design_lessons")
async def design_lessons(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "design_lessons.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "📹 Хочешь научиться основам дизайна и начать свой длинный и увлекательный путь в этом направлении?\n\n"
        "👇 Наши бесплатные уроки помогут тебе сделать это!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Посмотреть уроки", url=f"{DESIGN_LESSONS_LINK}")], # поменять ссылку на нужную ссылку с уроками
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_free_products")]
    ])
    await callback.message.edit_media(
        media=InputMediaPhoto(media=image, caption=caption),
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "editing_lessons")
async def editing_lessons(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "editing_lessons.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "🎞 Хочешь монтировать видео как боженька и быть круче, чем самые крутые тиктокеры?\n\n"
        "👇 Наши уроки помогут тебе в этом, заглядывай туда!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Посмотреть уроки", url=f"{EDITING_LESSONS_LINK}")], # поменять ссылку на нужную ссылку с уроками
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_free_products")]
    ])
    await callback.message.edit_media(
        media=InputMediaPhoto(media=image, caption=caption),
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "design_consult")
async def design_consult(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "design_consult.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "Хочешь получить консультацию от профессионалов в области и наметить себе план развития?\n\n"
        "👇 Записывайся на консультацию у нашего менеджера!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Договориться о консультации", url=f"https://t.me/{MANAGER_USERNAME[1:]}")], # поменять ссылку на менеджера
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_free_products")]
    ])
    await callback.message.edit_media(
        media=InputMediaPhoto(media=image, caption=caption),
        reply_markup=kb
    )
    await callback.answer()

@router.message(F.text == "👀 О нас")
async def about_us(message: Message):
    image_path = BASE_DIR / "media" / "about_us.jpg"
    if not image_path.exists():
        await message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "💬 Давай мы расскажем немного о себе. Выбери, что тебя интересует?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Кто мы такие?", callback_data="who_are_we")],
        [InlineKeyboardButton(text="Почему мы?", callback_data="why_us")],
        [InlineKeyboardButton(text="Портфолио", callback_data="portfolio")],
        [InlineKeyboardButton(text="FAQ", callback_data="faq")]
    ])
    await message.answer_photo(
        photo=image,
        caption=caption,
        reply_markup=kb
    )

@router.callback_query(F.data == "who_are_we")
async def who_are_we(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "who_are_we.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "Мы - контент-студия полного цикла, которая предоставляет услуги по различным направлениям, например:\n"
        "1. Программирование\n"
        "2. Дизайн\n"
        "3. Монтаж рилсов\n\n"
        "Да и вообще для каждого вашего вопроса мы найдём ответ, если достаточно заплатите!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="А что по ценникам?", callback_data="more_who_are_we_1")]
    ])
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image,
        caption=caption,
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "more_who_are_we_1")
async def who_are_we(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "more_who_are_we.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "Решение мы можем найти для любого кармана, главное - обсудить сроки, детали и количество правок!\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Какое отношение к клиентам?", callback_data="more_who_are_we_2")]
    ])
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image,
        caption=caption,
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "more_who_are_we_2")
async def who_are_we(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "more_who_are_we_2.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "К каждому клиенту - индивидуальный подход, мы любим всех и никого не обижаем, если бы вы знали, как мы вас любим - вы бы расплакались!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пойду делать заказ!", callback_data="go_main_menu")]
    ])
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image,
        caption=caption,
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "portfolio")
async def portfolio(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "portfolio.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "Хочешь посмотреть на работы наших ребят? Ну, так погнали! Нажимай на кнопку ниже, переходи и любуйся!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Смотреть портфолио!", url=f"{PORTFOLIO_LINK}")]
    ])
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image,
        caption=caption,
        reply_markup=kb
    )

@router.callback_query(F.data == "faq")
async def faq(callback: CallbackQuery):
    image_path = BASE_DIR / "media" / "faq.jpg"
    if not image_path.exists():
        await callback.message.answer("⚠️ Картинка не найдена.")
        return
    image = FSInputFile(image_path)
    caption = (
        "❓ ВОПРОСЫ, КОТОРЫЕ НАМ ЧАСТО ЗАДАЮТ\n\n"
        "1️⃣ Чем занимается Контент-студия \"КОТИКОВ\"?\n"
        "Мы создаём эффективный контент: видео, дизайн, иллюстрации и программные решения для тех, кто хочет влиять на аудиторию.\n\n"
        "2️⃣ Какие услуги вы предлагаете?\n"
        "Монтаж видео, графический дизайн, иллюстрирование, разработка чат-ботов и интерфейсов — полный комплекс для продвижения бренда.\n\n"
        "3️⃣ Могу ли я заказать у вас только одну услугу?\n"
        "Конечно! Выбирайте то, что нужно именно вам — мы гибко подстраиваемся под задачи.\n\n"
        "4️⃣ Как быстро вы делаете проекты?\n"
        "Сроки зависят от объёма, но мы всегда ориентируемся на ваш дедлайн и стараемся работать максимально оперативно.\n\n"
        "5️⃣ Сколько стоит проект?\n"
        "Цена рассчитывается индивидуально — зависит от сложности и объёма работы. Минимальная стоимость от 1000 рублей.\n\n"
        "6️⃣ Как начать сотрудничество?\n"
        "Свяжитесь с нами через Telegram или оставьте заявку через Котикова младшего — мы быстро ответим и поможем с брифом.\n\n"
        "7️⃣ Чем отличается раздел выбора \"Услуг и тарифов\" от раздела \"Сделать заказ\"?\n"
        "В разделе \"Услуги и тарифы\" мы предлагаем вам быстрые и готовые решения, а в разделе \"Сделать заказ\" вы можете оформить заказ по своему брифу, если ни одно из предложенных нами направлений работы не соответствует вашим желаниям.\n\n"
        "8️⃣ Мяукаете?\n"
        "Да, мяуканье от команды можно приобрести от 1000 р.\n\n"
        "💬 Если остались вопросы — пиши прямо сюда или в личные сообщения. Мы всегда на связи!"
    )
    caption_2 = (
        f"Почта: {EMAIL}\n"
        f"Аккаунт менеджера: {MANAGER_USERNAME}\n"
        f"Номер телефона: {PHONE_NUMBER}"
    )
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=image
    )
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=caption
    )
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=caption_2
    )

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
