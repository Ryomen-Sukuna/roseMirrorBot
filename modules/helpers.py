from subprocess import Popen, PIPE
from config import bot, OWNER_ID
import telethon
from modules.db import is_auth
import datetime


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def format_time(time):
    return str(datetime.timedelta(seconds=time))


def run_shell(command: str, wait: bool):
    subproc = Popen(command, stdout=PIPE, stderr=PIPE,
                    shell=True, universal_newlines=True)
    if not wait:
        return subproc
    stdout, stderr = subproc.communicate()
    return stdout, stderr


def hnd(**args):
    args["pattern"] = "^(?i)[?/!]" + args["pattern"] + \
        "(?: |$|@roseMirrorBot)(.*)"

    def decorator(func):
        async def wrapper(ev):
            try:
                await func(ev)
            except Exception as e:
                await ev.reply(str(e))
        bot.add_event_handler(wrapper, telethon.events.NewMessage(**args))
        return func
    return decorator


def auth_only(func):
    async def wrapper(ev):
        if (
            ev.is_private
            and is_auth(ev.sender_id)
            or not ev.is_private
            and is_auth(ev.chat_id)
        ):
            await func(ev)
        else:
            await ev.reply("You are not authorized to use this command.")
    return wrapper


def master_only(func):
    async def wrapper(ev):
        if ev.sender_id == OWNER_ID:
            await func(ev)
        else:
            await ev.reply("You are not authorized to use this command.")
    return wrapper
