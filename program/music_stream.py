import re
import asyncio

from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, Message

from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.exceptions import NoAudioSourceFound, NoActiveGroupCall, GroupCallNotFound

from program import LOGS
from program.utils.inline import stream_markup
from driver.design.thumbnail import thumb
from driver.design.chatname import CHAT_TITLE
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.core import calls, user, me_user
from driver.utils import bash, remove_if_exists, from_tg_get_msg
from driver.database.dbqueue import add_active_chat, remove_active_chat, music_on
from driver.decorators import require_admin, check_blacklist

from config import BOT_USERNAME, IMG_1, IMG_2, IMG_5
from asyncio.exceptions import TimeoutError
from youtubesearchpython import VideosSearch


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = data["thumbnails"][0]["url"]
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0

async def ytdl(link: str):
    stdout, stderr = await bash(
        f'yt-dlp --geo-bypass -g -f "[height<=?720][width<=?1280]" {link}'
    )
    if stdout:
        return 1, stdout
    return 0, stderr

def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


async def play_tg_file(c: Client, m: Message, replied: Message = None, link: str = None):
    chat_id = m.chat.id
    user_id = m.from_user.id
    if link:
        try:
            replied = await from_tg_get_msg(link)
        except Exception as e:
            LOGS.info(e)
            return await m.reply_text(f"» ᴇʀʀᴏʀ:\n\n» {e}")
    if not replied:
        return await m.reply(
            "» ʀᴇᴩʟʏ ᴛᴏ ᴀɴ **ᴀᴜᴅɪᴏ ғɪʟᴇ** ᴏʀ **ᴛʏᴩᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ.**"
        )
    if replied.audio or replied.voice:
        if not link:
            suhu = await replied.reply("» ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...")
        else:
            suhu = await m.reply("» ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...")
        dl = await replied.download()
        link = replied.link
        songname = "music"
        thumbnail = f"{IMG_5}"
        duration = "00:00"
        try:
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:80]
                else:
                    songname = replied.audio.file_name[:80]
                if replied.audio.thumbs:
                    if not link:
                        thumbnail = await c.download_media(replied.audio.thumbs[0].file_id)
                    else:
                        thumbnail = await user.download_media(replied.audio.thumbs[0].file_id)
                duration = convert_seconds(replied.audio.duration)
            elif replied.voice:
                songname = "voice note"
                duration = convert_seconds(replied.voice.duration)
        except BaseException:
            pass

        if not thumbnail:
            thumbnail = f"{IMG_5}"

        if chat_id in QUEUE:
            await suhu.edit("» ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ...")
            gcname = m.chat.title
            ctitle = await CHAT_TITLE(gcname)
            title = songname
            userid = m.from_user.id
            image = await thumb(thumbnail, title, userid, ctitle)
            pos = add_to_queue(chat_id, songname, dl, link, "music", 0)
            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
            buttons = stream_markup(user_id)
            await suhu.delete()
            await m.reply_photo(
                photo=image,
                reply_markup=InlineKeyboardMarkup(buttons),
                caption=f"😴 **ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ** `{pos}`\n\n"
                        f"📌 **ᴛɪᴛʟᴇ:** [{songname}]({link}) | `ᴀᴜᴅɪᴏ`\n"
                        f"🕛 **ᴅᴜʀᴀᴛɪᴏɴ:** `{duration}`\n"
                        f"😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
            )
            remove_if_exists(image)
        else:
            try:
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                title = songname
                userid = m.from_user.id
                image = await thumb(thumbnail, title, userid, ctitle)
                await suhu.edit(
                            f"**Downloader**\n100% ████████████100%\n\n**Time Taken**: 00:00 Seconds\n\n**Converting Audio[FFmpeg Process]**"
                        )
                await music_on(chat_id)
                await add_active_chat(chat_id)
                await calls.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                        HighQualityAudio(),
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "music", 0)
                await suhu.delete()
                buttons = stream_markup(user_id)
                requester = (
                    f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                )
                await m.reply_photo(
                    photo=image,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"📌 **ᴛɪᴛʟᴇ:** [{songname}]({link}) | `ᴀᴜᴅɪᴏ`\n"
                            f"🕛 **ᴅᴜʀᴀᴛɪᴏɴ:** `{duration}`\n"
                            f"😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                )
                remove_if_exists(image)
            except (NoActiveGroupCall, GroupCallNotFound):
                await suhu.delete()
                await remove_active_chat(chat_id)
                await m.reply_text("» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇᴄʜᴀᴛ ғᴏᴜɴᴅ !")
            except Exception as e:
                LOGS.info(e)
    else:
        await m.reply_text(
            "» ʀᴇᴩʟʏ ᴛᴏ ᴀɴ **ᴀᴜᴅɪᴏ ғɪʟᴇ** ᴏʀ **ɢɪᴠᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ.**"
        )


@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats", "can_delete_messages", "can_invite_users"], self=True)
async def audio_stream(c: Client, m: Message):
    await m.delete()
    replied = m.reply_to_message
    chat_id = m.chat.id
    user_id = m.from_user.id
    if m.sender_chat:
        return await m.reply_text(
            "ʏᴏᴜ'ʀᴇ ᴀɴ __ᴀɴᴏɴʏᴍᴏᴜs__ ᴜsᴇʀ !\n\n» ʀᴇᴠᴇʀᴛ ʙᴀᴄᴋ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴛᴏ ᴜsᴇ ᴍᴇ."
        )
    try:
        ubot = me_user.id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "banned":
            try:
                await m.reply_text("» ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ, ᴜɴʙᴀɴ ʜᴇʀ ᴛᴏ ᴩʀᴏᴄᴇᴇᴅ !")
                await remove_active_chat(chat_id)
            except BaseException:
                pass
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
    except UserNotParticipant:
        try:
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            LOGS.info(e)
            return await m.reply_text(
                f"» **ᴀssɪsᴛᴀɴᴛ ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ**\n\n**ʀᴇᴀsᴏɴ**: `{e}`"
            )
    if replied:
        if replied.audio or replied.voice:
            await play_tg_file(c, m, replied)
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» ʀᴇᴩʟʏ ᴛᴏ ᴀɴ **ᴀᴜᴅɪᴏ ғɪʟᴇ** ᴏʀ **ᴛʏᴩᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ.**"
                )
            else:
                suhu = await query.answer("commands menu")   
                suhu = await c.send_message(chat_id, "**Downloading**\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("» **ɴᴏᴛ ғᴏᴜɴᴅ.**")
                else:
                    songname = search[0]
                    title = search[0]
                    url = search[1]
                    duration = search[2]
                    thumbnail = search[3]
                    userid = m.from_user.id
                    gcname = m.chat.title
                    ctitle = await CHAT_TITLE(gcname)
                    image = await thumb(thumbnail, title, userid, ctitle)
                    out, ytlink = await ytdl(url) 
                    if out == 0:
                        await suhu.edit(f"» ʏᴛ-ᴅʟ ɪssᴜᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ \n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            await suhu.edit("» ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ...")
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "music", 0
                            )
                            await suhu.delete()
                            buttons = stream_markup(user_id)
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=image,
                                reply_markup=InlineKeyboardMarkup(buttons),
                                caption=f"😴 **ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ** `{pos}`\n\n📌 **ᴛɪᴛʟᴇ:** [{songname}]({url}) | `ᴀᴜᴅɪᴏ`\n**🕛 ᴅᴜʀᴀᴛɪᴏɴ:** `{duration}`\n😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                            )
                            remove_if_exists(image)
                        else:
                            try:
                                await suhu.edit(
                            f"**Downloader**\n100% ████████████100%\n\n**Time Taken**: 00:00 Seconds\n\n**Converting Audio[FFmpeg Process]**"
                        )
                                await music_on(chat_id)
                                await add_active_chat(chat_id)
                                await calls.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                                await suhu.delete()
                                buttons = stream_markup(user_id)
                                requester = (
                                    f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                )
                                await m.reply_photo(
                                    photo=image,
                                    reply_markup=InlineKeyboardMarkup(buttons),
                                    caption=f"📌 **ᴛɪᴛʟᴇ:** [{songname}]({url}) | `ᴀᴜᴅɪᴏ`\n**🕛 ᴅᴜʀᴀᴛɪᴏɴ:** `{duration}`\n😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                                )
                                remove_if_exists(image)
                            except (NoActiveGroupCall, GroupCallNotFound):
                                await suhu.delete()
                                await remove_active_chat(chat_id)
                                await m.reply_text("» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇᴄʜᴀᴛ ғᴏᴜɴᴅ !")
                            except NoAudioSourceFound:
                                await suhu.delete()
                                await remove_active_chat(chat_id)
                                await m.reply_text("» ɴᴏ ᴀᴜᴅɪᴏ sᴏᴜʀᴄᴇ ғᴏᴜɴᴅ.")
    else:
        if len(m.command) < 2:
            await m.reply(
                "» ʀᴇᴩʟʏ ᴛᴏ ᴀɴ **ᴀᴜᴅɪᴏ ғɪʟᴇ** ᴏʀ **ᴛʏᴩᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ.**"
            )
        elif "t.me" in m.command[1]:
            for i in m.command[1:]:
                if "t.me" in i:
                    await play_tg_file(c, m, link=i)
                continue
        else:
            suhu = await c.send_message(chat_id, "**Downloading**\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await suhu.edit("» **ɴᴏᴛ ғᴏᴜɴᴅ****")
            else:
                songname = search[0]
                title = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                userid = m.from_user.id
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                image = await thumb(thumbnail, title, userid, ctitle)
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await suhu.edit(f"» ʏᴛ-ᴅʟ ɪssᴜᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ \n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        await suhu.edit("» ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ...")
                        pos = add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                        await suhu.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        buttons = stream_markup(user_id)
                        await m.reply_photo(
                            photo=image,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            caption=f"» ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ** `{pos}`\n\n📌 **ᴛɪᴛʟᴇ:** [{songname}]({url}) | `ᴀᴜᴅɪᴏ`\n**🕛 ᴅᴜʀᴀᴛɪᴏɴ:** `{duration}`\n😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                        )
                        remove_if_exists(image)
                    else:
                        try:
                            await suhu.edit("» ᴩʀᴏᴄᴇssɪɴɢ...")
                            await music_on(chat_id)
                            await add_active_chat(chat_id)
                            await calls.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            buttons = stream_markup(user_id)
                            await m.reply_photo(
                                photo=image,
                                reply_markup=InlineKeyboardMarkup(buttons),
                                caption=f"📌 **ᴛɪᴛʟᴇ:** [{songname}]({url}) | `ᴀᴜᴅɪᴏ`\n**🕛 ᴅᴜʀᴀᴛɪᴏɴ:** `{duration}`\n😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                            )
                            remove_if_exists(image)
                        except (NoActiveGroupCall, GroupCallNotFound):
                            await suhu.delete()
                            await remove_active_chat(chat_id)
                            await m.reply_text("» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇᴄʜᴀᴛ ғᴏᴜɴᴅ !")
                        except NoAudioSourceFound:
                            await suhu.delete()
                            await remove_active_chat(chat_id)
                            await m.reply_text("» ɴᴏ ᴀᴜᴅɪᴏ sᴏᴜʀᴄᴇ ғᴏᴜɴᴅ...")


@Client.on_message(command(["stream", f"stream@{BOT_USERNAME}"]) & other_filters)
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats", "can_delete_messages", "can_invite_users"], self=True)
async def live_music_stream(c: Client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    user_id = m.from_user.id
    if m.sender_chat:
        return await m.reply_text(
            "ʏᴏᴜ'ʀᴇ ᴀɴ __ᴀɴᴏɴʏᴍᴏᴜs__ ᴜsᴇʀ !\n\n» ʀᴇᴠᴇʀᴛ ʙᴀᴄᴋ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴛᴏ ᴜsᴇ ᴍᴇ."
        )
    try:
        ubot = me_user.id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "banned":
            try:
                await m.reply_text("» ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ, ᴜɴʙᴀɴ ʜᴇʀ ᴛᴏ ᴩʀᴏᴄᴇᴇᴅ !")
                await remove_active_chat(chat_id)
            except BaseException:
                pass
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
    except UserNotParticipant:
        try:
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            LOGS.info(e)
            return await m.reply_text(
                f"» **ᴀssɪsᴛᴀɴᴛ ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ**\n\n**ʀᴇᴀsᴏɴ**: `{e}`"
            )
    if len(m.command) < 2:
        await m.reply_text("» ɢɪᴠᴇ ᴀ ʏᴏᴜᴛᴜʙᴇ ʟɪᴠᴇ ᴠɪᴅᴇᴏ url/m3u8 ʟɪɴᴋ ᴛᴏ sᴛʀᴇᴀᴍ.")
    else:
        url = m.text.split(None, 1)[1]
        msg = await m.reply_text("🔎")
        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, url)
        if match:
            coda, data = await ytdl(url)
        else:
            data = url
            coda = 1
        if coda == 0:
            await msg.edit_text(f"» ʏᴛ-ᴅʟ ɪssᴜᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ \n\n» `{data}`")
        else:
            if "m3u8" in url:
                if chat_id in QUEUE:
                    await msg.edit_text("» ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ...")
                    pos = add_to_queue(chat_id, "m3u8 audio", data, url, "music", 0)
                    await msg.delete()
                    requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    buttons = stream_markup(user_id)
                    await m.reply_photo(
                        photo=f"{IMG_1}",
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=f"» ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ** `{pos}`\n\n📌 **ᴛɪᴛʟᴇ:** [m3u8 audio stream]({url}) | `ʟɪᴠᴇ`\n😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                    )
                else:
                    try:
                        await msg.edit_text("» ᴩʀᴏᴄᴇssɪɴɢ...")
                        await music_on(chat_id)
                        await add_active_chat(chat_id)
                        await calls.join_group_call(
                            chat_id,
                            AudioPiped(
                                data,
                                HighQualityAudio(),
                            ),
                            stream_type=StreamType().live_stream,
                        )
                        add_to_queue(chat_id, "m3u8 audio", data, url, "music", 0)
                        await msg.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        buttons = stream_markup(user_id)
                        await m.reply_photo(
                            photo=f"{IMG_2}",
                            reply_markup=InlineKeyboardMarkup(buttons),
                            caption=f"📌 **ᴛɪᴛʟᴇ:** [m3u8 audio stream]({url}) | `ʟɪᴠᴇ`\n😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                        )
                    except (NoActiveGroupCall, GroupCallNotFound):
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇᴄʜᴀᴛ ғᴏᴜɴᴅ !")
                    except NoAudioSourceFound:
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("» ɴᴏ ᴀᴜᴅɪᴏ sᴏᴜʀᴄᴇ ғᴏᴜɴᴅ.")
            else:
                search = ytsearch(url)
                title = search[0]
                songname = search[0]
                thumbnail = search[3]
                userid = m.from_user.id
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                image = await thumb(thumbnail, title, userid, ctitle)
                if chat_id in QUEUE:
                    await msg.edit_text("» ᴀᴅᴅɪɴɢ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ...")
                    pos = add_to_queue(chat_id, songname, data, url, "music", 0)
                    await msg.delete()
                    requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    buttons = stream_markup(user_id)
                    await m.reply_photo(
                        photo=image,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=f"» ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ** `{pos}`\n\n📌 **ᴛɪᴛʟᴇ:** [{songname}]({url}) | `ʟɪᴠᴇ`\n😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                    )
                    remove_if_exists(image)
                else:
                    try:
                        await msg.edit_text("» ᴩʀᴏᴄᴇssɪɴɢ...")
                        await music_on(chat_id)
                        await add_active_chat(chat_id)
                        await calls.join_group_call(
                            chat_id,
                            AudioPiped(
                                data,
                                HighQualityAudio(),
                            ),
                            stream_type=StreamType().live_stream,
                        )
                        add_to_queue(chat_id, songname, data, url, "music", 0)
                        await msg.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        buttons = stream_markup(user_id)
                        await m.reply_photo(
                            photo=image,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            caption=f"📌 **ᴛɪᴛʟᴇ:** [{songname}]({url}) | `ʟɪᴠᴇ`\n😘 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {requester}",
                        )
                        remove_if_exists(image)
                    except (NoActiveGroupCall, GroupCallNotFound):
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇᴄʜᴀᴛ ғᴏᴜɴᴅ !")
                    except NoAudioSourceFound:
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("» ɴᴏ ᴀᴜᴅɪᴏ sᴏᴜʀᴄᴇ ғᴏᴜɴᴅ.")
                    except TimeoutError:
                        await msg.delete()
                        await remove_active_chat(chat_id)
                        await m.reply_text("sᴛʀᴇᴀᴍ ᴄᴀɴᴄᴇʟʟᴇᴅ, ᴩʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴜsᴇ `/vstream` ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ sᴛʀᴇᴀᴍ.")
