import subprocess
import os
from .helpers import TEMP_DOWNLOAD_PATH, hnd, auth_only, EDIT_SLEEP
import asyncio


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
            if file_path.endswith(".mkv"):
                mp4_path = file_path[:-4] + ".mp4"
                proc = subprocess.Popen(['ffmpeg', '-i', file_path, mp4_path],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                for line in proc.stdout:
                    event = await edit_ffmpeg_progress(event, line, file_path)
                os.remove(file_path)
                return mp4_path
    return None


async def edit_ffmpeg_progress(event, progress, file_name):
    if event.text != f"Converting {file_name} | {progress}":
        m = await event.edit(f"Converting {file_name} | {progress}")
    await asyncio.sleep(EDIT_SLEEP)
    return m


@hnd(pattern="convert")
@auth_only
async def convert(event):
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
        file_name = reply_message.document.file_name
        if file_name.endswith(".mkv"):
            file_path = os.path.join(TEMP_DOWNLOAD_PATH, file_name)
            await reply_message.download(file_path)
            msg = await event.edit("Converting...")
            mp4_path = await mkv_to_mp4(file_path, msg)
            if mp4_path:
                await event.reply(file=mp4_path)
                os.remove(mp4_path)
            else:
                await event.reply("Failed to convert to mp4.")
        else:
            await event.reply("Reply to a mkv file to convert it to mp4.")
            return
    else:
        await event.reply("Reply to a file to convert it to mp4.")
        return
