import asyncio

from datetime import datetime
from sys import version_info
from time import time

from config import (
    ALIVE_IMG,
    ALIVE_NAME,
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_USERNAME,
    UPDATES_CHANNEL,
)

from program import __version__, LOGS
from pytgcalls import (__version__ as pytover)

from driver.filters import command
from driver.core import bot, me_bot, me_user
from driver.database.dbusers import add_served_user
from driver.database.dbchat import add_served_chat, is_served_chat
from driver.database.dblockchat import blacklisted_chats
from driver.database.dbpunish import is_gbanned_user
from driver.decorators import check_blacklist

from pyrogram import Client, filters, __version__ as pyrover
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest

__major__ = 0
__minor__ = 2
__micro__ = 1

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("weeks", 60 * 60 * 24 * 7),
    ("days", 60 * 60 * 24),
    ("h", 60 * 60),
    ("m", 60),
    ("s", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{}{}{}".format(amount, unit, "" if amount == 1 else ""))
    return ":".join(parts)


@Client.on_message(
    command(["start", f"start@{BOT_USERNAME}"]) & filters.private & ~filters.edited
)
@check_blacklist()
async def start_(c: Client, message: Message):
    user_id = message.from_user.id
    await add_served_user(user_id)
    await message.reply_text(
        f"""🖤 **ʜᴇʏ {message.from_user.mention()} !\n
   ✨ ɪ ᴀᴍ [{me_bot.first_name}](https://t.me/{me_bot.username}) ᴀ ᴍᴜsɪᴄ ᴩʟᴀʏᴇʀ ʙᴏᴛ ᴍᴀᴅᴇ ғᴏʀ ᴩʟᴀʏɪɴɢ ᴀᴜᴅɪᴏs ᴀɴᴅ ᴠɪᴅᴇᴏs ɪɴ ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏᴄʜᴀᴛs.

 📍 ᴀʟʟ ᴏғ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ʟɪsᴛᴇᴅ ɪɴ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ, ᴄʟɪᴄᴋ ᴏɴ ɪᴛ ᴛᴏ ᴋɴᴏᴡ ᴀʟʟ ᴏғ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs.** 🥱
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ ➕", url=f"https://t.me/{me_bot.username}?startgroup=true")
                ],[
                    InlineKeyboardButton("• ʜᴇʟᴩ •", callback_data="command_list"),
                    InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about_me") 
                ],[
                    InlineKeyboardButton("• ᴍᴀɪɴᴛᴀɪɴᴇʀ •", url=f"https://t.me/Xd_LyF"),
                    InlineKeyboardButton("• sᴜᴩᴩᴏʀᴛ •", url=f"https://t.me/{GROUP_SUPPORT}")
                ],[
                    InlineKeyboardButton("• sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ •", url="https://t.me/Xd_About")
                ],
            ]
        ),
        disable_web_page_preview=True,
    )


@Client.on_message(
    command(["alive", f"alive@{BOT_USERNAME}"]) & filters.group & ~filters.edited
)
@check_blacklist()
async def alive(c: Client, message: Message):
    chat_id = message.chat.id
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("• sᴜᴩᴩᴏʀᴛ •", url=f"https://t.me/{GROUP_SUPPORT}"),
                InlineKeyboardButton(
                    "Oᴡɴᴇʀ", url="tg://user?id=1920507972"
                ),
            ]
        ]
    )
    text = f"**ʜᴇʏ {message.from_user.mention()},\n\n   ɪ'ᴍ {me_bot.first_name}**\n\n🖤 ᴅᴇᴠᴇʟᴏᴩᴇʀ: [这 ⏤͟͟͞Ftw™](https://t.me/Xd_LyF\n🤯 ʙᴏᴛ ᴠᴇʀsɪᴏɴ: `v{__version__}`\n🔥 ᴩʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ: `{pyrover}`\n🐍 ᴩʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ: `{__python_version__}`\n✨ ᴩʏ∆ᴛɢᴄᴀʟʟs ᴠᴇʀsɪᴏɴ: `{pytover.__version__}`\n🥱 ᴜᴩᴛɪᴍᴇ: `{uptime}`\n"
    await c.send_photo(
        chat_id,
        photo=f"{ALIVE_IMG}",
        caption=text,
        reply_markup=buttons,
    )


@Client.on_message(command(["ping", f"ping@{BOT_USERNAME}"]) & ~filters.edited)
@check_blacklist()
async def ping_pong(c: Client, message: Message):
    start = time()
    delta_ping = time() - start
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    pingtext = "pong ping !"
    response = await message.reply_photo(
        photo="https://telegra.ph/file/3d245c9fa9e2c7851cc8f.jpg",
        caption=pingtext,
    )
    await response.edit_text(text="🏓 **ᴩᴏɴɢ !**\n" f"⚡ `{delta_ping * 1000:.3f} ᴍs`\n\n<b><u>{me_bot.first_name} sʏsᴛᴇᴍ sᴛᴀᴛs:</u></b>\n• ᴜᴩᴛɪᴍᴇ : {uptime}\n• ᴠᴇʀsɪᴏɴ : `v{__version__}`\n• ᴩʏᴛʜᴏɴ : `{__python_version__}`\n• ᴩʏʀᴏɢʀᴀᴍ : `{pyrover}`\n• ᴩʏ∆ᴛɢᴄᴀʟʟs : `{pytover.__version__}`")

@Client.on_message(command(["uptime", f"uptime@{BOT_USERNAME}"]) & ~filters.edited)
@check_blacklist()
async def get_uptime(c: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        f"• ᴜᴩᴛɪᴍᴇ: `{uptime}`\n"
        f"• sᴛᴀʀᴛ ᴛɪᴍᴇ: `{START_TIME_ISO}`"
    )


@Client.on_chat_join_request()
async def approve_join_chat(c: Client, m: ChatJoinRequest):
    if not m.from_user:
        return
    try:
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)
    except FloodWait as e:
        await asyncio.sleep(e.x + 2)
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)


@Client.on_message(filters.new_chat_members)
async def new_chat(c: Client, m: Message):
    chat_id = m.chat.id
    if await is_served_chat(chat_id):
        pass
    else:
        await add_served_chat(chat_id)
    for member in m.new_chat_members:
        try:
            if member.id == me_bot.id:
                if chat_id in await blacklisted_chats():
                    await m.reply_text(
                        "» ᴛʜɪs ᴄʜᴀᴛ ɪs ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ʙʏ ᴍʏ ᴇx, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ ʜᴇʀᴇ."
                    )
                    return await bot.leave_chat(chat_id)
            if member.id == me_bot.id:
                return await m.reply(
                    "ʜᴇʏ, ɪ ᴀᴍ **𝐀ɭ๏иє** !\n\n"
                    " ᴀ ᴍᴜsɪᴄ ᴩʟᴀʏᴇʀ ʙᴏᴛ ғᴏʀ ʏᴏᴜʀ ɢʀᴏᴜᴩ ᴠᴏɪᴄᴇᴄʜᴀᴛs, ᴩʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀs ᴀɴ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴀʟʟ ᴩᴇʀᴍɪssɪᴏɴs ᴇxᴄᴇᴩᴛ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ\n\n"
                    "ᴀғᴛᴇʀ ᴩʀᴏᴍᴏᴛɪɴɢ ᴍᴇ ᴀs ᴀɴ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴀʟʟ ᴩᴇʀᴍɪssɪᴏɴs ᴛʏᴩᴇ `/reload`",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("• sᴜᴩᴩᴏʀᴛ •", url=f"https://t.me/{GROUP_SUPPORT}"),
                                InlineKeyboardButton("• ᴀssɪsᴛᴀɴᴛ•", url=f"https://t.me/{me_user.username}")
                            ],[
                                InlineKeyboardButton("• ᴅᴇᴠᴇʟᴏᴩᴇʀ •", url=f"https://t.me/{OWNER_USERNAME}")
                            ]
                        ]
                    )
                )
            return
        except Exception:
            return


chat_watcher_group = 5

@Client.on_message(group=chat_watcher_group)
async def chat_watcher_func(_, message: Message):
    userid = message.from_user.id
    suspect = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_gbanned_user(userid):
        try:
            await message.chat.ban_member(userid)
        except ChatAdminRequired:
            LOGS.info(f"can't remove gbanned user from chat: {message.chat.id}")
            return
        await message.reply_text(
            f"👮🏼 (> {suspect} <)\n\nᴀ**ɢʙᴀɴɴᴇᴅ** ᴍᴏᴛʜᴇʀғᴜ*ᴋᴇʀ ᴅᴇᴛᴇᴄᴛᴇᴅ, ᴛʜᴀᴛ ᴍᴏᴛʜᴇʀғᴜ*ᴋᴇʀ ɪs ɢʙᴀɴɴᴇᴅ ʙʏ ᴍʏ ᴇx ᴀɴᴅ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴛʜɪs ᴄʜᴀᴛ !\n\n🚫 **ʀᴇᴀsᴏɴ:** ʙʜᴀᴅᴠᴀ sᴀᴀʟᴀ ʀᴀɴᴅɪʙᴀᴀᴢ."
        )
