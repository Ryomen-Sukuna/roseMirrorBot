import asyncio

from telethon import Button
from .helpers import auth_chat_only, run_shell, get_size, format_time, hnd
from .db import add_download_to_db, get_download_list, remove_download_from_db
from requests import get

import aria2p as aria2


def setup_aria():
    trackers_list = get(
        "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"
    ).text.replace("\n\n", ",")
    trackers = f"[{trackers_list}]"
    cmd = f"aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800 --max-connection-per-server=10 --rpc-max-request-size=1024M --check-certificate=false --follow-torrent=mem --seed-time=600 --max-upload-limit=0 --max-concurrent-downloads=1 --min-split-size=10M --follow-torrent=mem --split=10 --bt-tracker={trackers} --daemon=true --allow-overwrite=true"
    run_shell(cmd, wait=False)


setup_aria()
ARIA = aria2.API(aria2.Client(host="http://localhost", port=6800, secret=""))


def add_download(chat_id, url, path):
    download = ARIA.add_uris([url], options={"dir": path})
    add_download_to_db(chat_id, download.gid)
    return download


def get_path_from_chat_id(chat_id):
    return f"/downloads/{chat_id}/"


def get_len_downloads():
    return len(get_download_list())


def get_download_gids():
    downloads = ARIA.get_downloads()
    return [d.gid for d in downloads]


def gen_progress_msg(chat_id: int, status):
    msg = f"Downloading: {status.name}"
    msg += f"\nSpeed: {get_size(status.download_speed)}/s"
    msg += "\nETA: 0:00:00"
    msg += f"\nTotal: {get_size(status.total_length)}"
    msg += f"\nProgress: {status.progress}%"
    buttons = [
        [Button.inline("Cancel", data=f"cancel_{chat_id}_{status.gid}")],
        [Button.inline("Pause", data=f"pause_{chat_id}_{status.gid}")],
    ]
    return msg, buttons


async def progress_callback(gid: str, msg):
    finished = False
    while not finished:
        status = ARIA.get_download(gid)
        if status.status == "complete":
            finished = True
            buttons = [
                [Button.inline("Upload", data=f"upload_{status.gid}")],
                [Button.inline("Direct URL", data=f"url_{status.gid}")],
            ]
            msg = await msg.edit(
                f"Download complete.\nSaved to: `{status.files[0].path}`")
            remove_download_from_db(msg.chat_id, gid)
        elif status.status == "error":
            finished = True
            msg = await msg.edit("Download failed." +
                                 f"\nError: {status.error_message}")
            remove_download_from_db(msg.chat_id, gid)
        elif status.status == "paused":
            finished = True
            msg = await msg.edit("Download paused.")
        elif status.status == "active":
            msg = await msg.edit(gen_progress_msg(msg.chat_id, status))
            await asyncio.sleep(3)
        elif status.status == "waiting":
            msg = await msg.edit(gen_progress_msg(msg.chat_id, status))
            await asyncio.sleep(3)
        elif status.status == "stopped":
            buttons = [
                [Button.inline("Resume", data=f"start_{msg.chat_id}_{gid}")],
                [Button.inline("Delete", data=f"delete_{msg.chat_id}_{gid}")],
            ]
            msg = await msg.edit(
                f"Download stopped.",
                buttons=buttons,
            )
            finished = True
        else:
            msg = await msg.edit(f"Unknown status: {status.status}")
            finished = True


@hnd(pattern="download")
@auth_chat_only  # only allow users in the chat to download
async def download_cmd(ev):
    try:
        url = ev.text.split(" ", 1)[1]
    except IndexError:
        return await ev.reply("No URL provided")
    path = get_path_from_chat_id(ev.chat_id)
    download = add_download(ev.chat_id, url, path)
    msg = await ev.reply("`Downloading...`")
    await progress_callback(download.gid, msg)
