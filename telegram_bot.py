# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 16:59:50 2025

@author: zulfi
"""

import asyncio
import nest_asyncio
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv  # .env fayldan tokenni yuklash

nest_asyncio.apply()

# 📌 .env dan tokenni olish
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📌 JSON fayldan ma'lumotlarni yuklash
def load_videos():
    try:
        with open("videos.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def load_channels():
    try:
        with open("channels.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            channels = data.get("channels", [])
            print(f"🔵 Yuklangan kanallar: {channels}")
            return channels
    except FileNotFoundError:
        print("❌ channels.json topilmadi!")
        return []

# 📌 Video yuklab, `file_id` olish
@dp.message(lambda message: message.video) 
async def get_file_id(message: types.Message):
    file_id = message.video.file_id
    await message.reply(f"📌 Yangi `file_id`: `{file_id}`")
    print(f"📌 Yangi `file_id`: {file_id}")

# 📌 Kanallarni JSON fayldan yuklash
REQUIRED_CHANNELS = load_channels()  

# 📌 Inline keyboard tugmalarini yaratish
def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=channel["name"], url=f"https://t.me/{channel['username'][1:]}")]
            for channel in load_channels()
        ]
    )
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="check_subscription")]
    )
    return keyboard

# 🎯 `/start` buyruqni ushlash
@dp.message(Command("start"))
async def start_command(message: types.Message):
    print("🟢 /start bosildi!") 
    user_id = message.from_user.id
    not_subscribed = []
    channels = load_channels()  

    if not channels:
        await message.answer("❌ Hech qanday kanal sozlanmagan! Admin tekshirishi kerak.")
        return
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel["name"])
        except Exception as e:
            print(f"⚠️ Xatolik: {e}")
            continue

    if not_subscribed:
        await message.answer(
            "❌ Kechirasiz, botdan foydalanish uchun quyidagi kanallarga obuna bo‘lishingiz kerak:",
            reply_markup=get_subscription_keyboard()
        )
    else:
        await message.answer("🎬 Salom! Kino kodini yuboring va men sizga kinoni yuboraman.")

# 📌 Foydalanuvchi "✅ Tasdiqlash" tugmasini bossa, tekshirish
@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    not_subscribed = []
    channels = load_channels()  

    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel["name"])
        except Exception as e:
            print(f"⚠️ Xatolik: {e}")
            continue

    if not_subscribed:
        await callback_query.message.edit_text(
            "❌ Kechirasiz, hali barcha kanallarga a'zo bo‘lmadingiz. Iltimos, avval obuna bo‘ling.",
            reply_markup=get_subscription_keyboard()
        )
    else:
        await callback_query.message.edit_text("✅ Rahmat! Endi botdan foydalanishingiz mumkin.")

# 🎯 Kino kodi yuborilganda, video + tavsif jo‘natish
@dp.message(lambda message: isinstance(message.text, str) and message.text.isdigit())
async def send_video(message: types.Message):
    user_id = message.from_user.id
    not_subscribed = []
    channels = load_channels()  

    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel["name"])
        except Exception as e:
            print(f"⚠️ Xatolik: {e}")
            continue

    if not_subscribed:
        await message.answer(
            "❌ Kechirasiz, botdan foydalanish uchun quyidagi kanallarga obuna bo‘lishingiz kerak:",
            reply_markup=get_subscription_keyboard()
        )
        return
    
    video_mapping = load_videos()  
    video_data = video_mapping.get(message.text)
    
    if video_data:
        await bot.send_video(
            chat_id=message.chat.id,
            video=video_data["file_id"],
            caption=video_data["description"],
            supports_streaming=True,  # 🚀 🔹 Foydalanuvchi faqat tomosha qiladi
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
