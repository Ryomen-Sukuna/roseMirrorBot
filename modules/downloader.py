from helpers import run_shell
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


def add_download(url, path):
    ARIA.add_uris([url], options={"dir": path})


def get_path_from_chat_id(chat_id):
    return f"/downloads/{chat_id}/"
