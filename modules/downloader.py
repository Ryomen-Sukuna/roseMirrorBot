from .helpers import run_shell, get_size, format_time
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

def gen_progress_msg(chat_id: int, gid: str):
    status = ARIA.get_download([gid])
    if status.status == "active":
        msg = f"Downloading: {status.files[0].name}"
        msg += f"\nSpeed: {get_size(status.download_speed)}/s"
        msg += f"\nETA: {format_time(status.eta)}"
        msg += f"\nTotal: {get_size(status.total_length)}"
        msg += f"\nProgress: {status.progress}%"
    elif status.status == "paused":
        msg = "Download paused."
    elif status.status == "error":
        msg = "Download failed."
    elif status.status == "complete":
        msg = "Download complete."
        msg += f"\nSaved to: `{status.files[0].path}`"
        remove_download_from_db(chat_id, gid)
    else:
        msg = "Download unknown status."
    return msg
