import subprocess
import os
from .helpers import TEMP_DOWNLOAD_PATH, hnd, auth_only, EDIT_SLEEP
import asyncio
from telethon import types


def IsFFmpegInstalled():
    try:
        subprocess.check_output(['ffmpeg', '-version'])
        return True
    except:
        return False


def IsFFprobeInstalled():
    try:
        subprocess.check_output(['ffprobe', '-version'])
        return True
    except:
        return False


async def mkv_to_mp4(file_path, event):
    if IsFFmpegInstalled():
        if os.path.isfile(file_path):
            frames = get_total_frames(file_path)
            if file_path.endswith(".mkv"):
                mp4_path = file_path[:-4] + ".mp4"
                cmd = "ffmpeg -i {} {} -progress pipe:1".format(
                    file_path, mp4_path)
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                prev_perc = 0
                for line in proc.stdout:
                    if "frame=" in line:
                        f = line.split("frame=")[1].split(" fps")[0].strip()
                        event, prev_perc = await edit_ffmpeg_progress(event, f, prev_perc, frames, file_path)
                        await asyncio.sleep(EDIT_SLEEP)
                os.remove(file_path)
                return mp4_path
    return None


async def edit_ffmpeg_progress(event, progress, prev_perc, frames, file_name):
    perc = calc_percent(int(progress), frames)
    if perc != prev_perc:
        file_name = file_name.split("/")[-1]
        MSG = f'''**Converting to MP4 | {perc}%**\n**File:** `{file_name}`\n**Frames:** `{progress}`/`{frames}`'''
        event = await event.edit(MSG)
    if perc == 100:
        await event.edit(f"**Conversion Complete!**\n**File:** `{file_name}`")
        return None, 0
    return event, perc


def calc_percent(current, total):
    return int(current * 100 / total)


def get_total_frames(file_path: str) -> int:
    if IsFFprobeInstalled():
        if os.path.isfile(file_path):
            cmd = 'ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -print_format json {}'.format(
                file_path)
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            stdout, _ = proc.communicate()
            frames = stdout.split('"nb_read_frames":')[
                1].split(',')[0].split('"')[1]
            return int(frames)
    else:
        return 0


def get_file_name(doc):
    for x in doc.attributes:
        if isinstance(x, types.DocumentAttributeFilename):
            return x.file_name
    return ""


@hnd(pattern="convert")
@auth_only
async def _convert(event):
    if event.is_private:
        await event.reply("This command is only available in groups.")
        return
    if not event.reply_to_msg_id:
        await event.reply("Reply to a file to convert it to mp4.")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.reply("Reply to a file to convert it to mp4.")
        return
    if reply_message.document:
        file_name = get_file_name(reply_message.document)
        if file_name.endswith(".mkv"):
            file_path = os.path.join(TEMP_DOWNLOAD_PATH, file_name)
            message = await event.reply("`Downloading...`")
            await reply_message.download_media(file_path)
            msg = await message.edit("`Converting...`")
            mp4_path = await mkv_to_mp4(file_path, msg)
            if mp4_path:
                async with event.client.action(event.chat_id, "video"):
                    await event.reply(file=mp4_path)
                os.remove(mp4_path)
            else:
                await event.reply("Failed to convert to mp4.")
        else:
            await event.reply("Reply to a mkv file to convert it to mp4.")
    else:
        await event.reply("Reply to a file to convert it to mp4.")
