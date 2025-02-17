# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 16:59:50 2025

@author: zulfi
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 16:48:16 2025

@author: zulfi
"""
import os  # 🔹 Faylning boshiga qo‘ying
import asyncio
import nest_asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

nest_asyncio.apply()

TOKEN = os.getenv("TOKEN")  # 🔹 TOKEN endi Railway'dan olinadi
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📌video junatib file id olish

@dp.message(lambda message: message.video) 
async def get_file_id(message: types.Message):
    file_id = message.video.file_id
    await message.reply(f"📌 Yangi `file_id`: `{file_id}`")
    print(f"📌 Yangi `file_id`: {file_id}")  # Terminalda ham chiqadi


# 📌 Tekshirish kerak bo‘lgan kanallar
REQUIRED_CHANNELS = [
    ("Kanal", "@yangi_kanal0208")
]

# 📌 Video mapping (kod → file_id + description)
VIDEO_MAPPING = {
    "230": {
        "file_id": "BAACAgIAAxkBAAMHZ6oSDreTOnGrDC1UeVMGj5-_UR4AAqJlAAL20lBJU-pj7ryHkxQ2BA",
        "description": "🎬 *Kino nomi:* Avengers: Endgame\n📆 *Yili:* 2019\n🎭 *Janr:* Fantastika, Harakat, Drama\n🕒 *Davomiyligi:* 3 soat 2 daqiqa\n⭐ *IMDB reytingi:* 8.4/10"
    },
    "231": {
        "file_id": "BAACAgIAAxkBAAMXZ6oVWL_QI-LjTQn7slUj5sQ43uUAAgZhAAJJ7XlIlbGXDfUJUn42BA",
        "description": "🎬 *Kino nomi:* Inception\n📆 *Yili:* 2010\n🎭 *Janr:* Fantastika, Triller\n🕒 *Davomiyligi:* 2 soat 28 daqiqa\n⭐ *IMDB reytingi:* 8.8/10"
    },
    "100": {
    "file_id": "BAACAgIAAxkBAANWZ6saiQdgKkol1u70Fu4cPcdU69oAAj5jAAISnWFJa5i0gHHrqZY2BA",
    "description": "🎬 *Kino nomi:* Yetimlar (Bekas)\n📆 *Yili:* 2012\n🌍 *Mamlakat:* Shvetsiya, Finlyandiya, Iroq\n🎭 *Janr:* Drama\n🕒 *Davomiyligi:* 97 daqiqa\n⭐ *IMDB reytingi:* 7.2/10"
}

    
    
    }
    

# 📌 Inline keyboard tugmalarini yaratish
def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=channel_name, url=f"https://t.me/{channel_link[1:]}")]
            for channel_name, channel_link in REQUIRED_CHANNELS
        ]
    )
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="check_subscription")]
    )
    return keyboard

# 🎯 `/start` buyruqni ushlash
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    not_subscribed = []
    
    # 📌 Foydalanuvchi barcha kanallarga obuna bo‘lganmi?
    for channel_name, channel_link in REQUIRED_CHANNELS:
        member = await bot.get_chat_member(chat_id=channel_link, user_id=user_id)
        if member.status not in ["member", "administrator", "creator"]:
            not_subscribed.append(channel_name)
    
    if not_subscribed:
        await message.answer(
            "❌ Kechirasiz, botimizdan foydalanishdan oldin ushbu kanallarga a'zo bo'lishingiz kerak.",
            reply_markup=get_subscription_keyboard()
        )
    else:
        await message.answer("🎬 Salom! Kino kodini yuboring va men sizga kinoni yuboraman.")

# 📌 Foydalanuvchi "✅ Tasdiqlash" tugmasini bossa, tekshirish
@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    not_subscribed = []

    # 📌 Yana tekshiramiz, foydalanuvchi a'zo bo‘lganmi?
    for channel_name, channel_link in REQUIRED_CHANNELS:
        member = await bot.get_chat_member(chat_id=channel_link, user_id=user_id)
        if member.status not in ["member", "administrator", "creator"]:
            not_subscribed.append(channel_name)

    if not_subscribed:
        await callback_query.message.edit_text(
            "❌ Kechirasiz, hali barcha kanallarga a'zo bo‘lmadingiz. Iltimos, avval obuna bo‘ling.",
            reply_markup=get_subscription_keyboard()
        )
    else:
        await callback_query.message.edit_text("✅ Rahmat! Endi botdan foydalanishingiz mumkin.")

# 🎯 Foydalanuvchi **kino kodi** yuborganda, video + matn jo‘natish
@dp.message(lambda message: isinstance(message.text, str) and message.text.isdigit())
async def send_video(message: types.Message):
    user_id = message.from_user.id
    not_subscribed = []

    # 📌 Kanalga obuna bo‘lganligini tekshirish
    for channel_name, channel_link in REQUIRED_CHANNELS:
        member = await bot.get_chat_member(chat_id=channel_link, user_id=user_id)
        if member.status not in ["member", "administrator", "creator"]:
            not_subscribed.append(channel_name)

    if not_subscribed:
        await message.answer(
            "❌ Kechirasiz, botdan foydalanish uchun avval kanalga obuna bo‘lishingiz kerak.",
            reply_markup=get_subscription_keyboard()
        )
        return
    
    # 🎬 Kino kodiga mos video topish
    video_data = VIDEO_MAPPING.get(message.text)
    if video_data:
        await bot.send_video(
            chat_id=message.chat.id,
            video=video_data["file_id"],
            caption=video_data["description"],
            parse_mode="Markdown"
        )
    else:
        await message.reply("❌ Kechirasiz, bu kodga mos video topilmadi.")

# 🚀 Botni ishga tushirish
async def main():
    print("✅ Bot ishga tushdi! Telegram’da sinab ko‘ring.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
