import psutil
import platform
import datetime

from modules.helpers import getUser, hnd, auth_only, master_only, get_size, format_time
from .downloader import get_len_downloads
import io
import sys
import asyncio
import traceback
from .db import add_auth


def get_system_statistics():
    STATS = "**System Statistics**\n"
    STATS += "• **OS:** `{}`\n".format(platform.platform())
    STATS += "• **CPU Cores**: " + str(psutil.cpu_count()) + "\n"
    STATS += "• **CPU Usage:** " + str(psutil.cpu_percent()) + "%\n"
    STATS += "• **RAM:** " + \
        str(get_size(psutil.virtual_memory().total)) + "\n"
    STATS += "• **RAM Usage:** " + str(psutil.virtual_memory().percent) + "%\n"
    STATS += "\n"
    STATS += "• **Disk:** " + \
        str(get_size(psutil.disk_usage("/").total)) + "\n"
    STATS += "• **Disk Usage:** " + str(psutil.disk_usage("/").percent) + "%\n"
    STATS += "• **Disk IO:** " + str(psutil.disk_io_counters().read_count) + " reads, " + str(
        psutil.disk_io_counters().write_count
    ) + " writes\n"
    STATS += "\n"
    STATS += "• **Network:** " + str(psutil.net_io_counters().bytes_sent) + " sent, " + str(
        psutil.net_io_counters().bytes_recv
    ) + " received\n"
    STATS += "\n"
    STATS += "• **Uptime:** " + \
        str(format_time(datetime.datetime.now() - psutil.boot_time())) + "\n"
    STATS += "• **Python:** " + str(sys.version) + "\n"
    STATS += "• **Downloads Count:** " + get_len_downloads() + "\n"

    return STATS


@hnd(pattern="sys")
@auth_only
async def sys_cmd(ev):
    await ev.reply(get_system_statistics())


@hnd(pattern="auth")
@master_only
async def auth_cmd(ev):
    user, _ = await getUser(ev)
    if not user and not ev.is_private:
        add_auth(ev.chat_id)
        await ev.reply("Chat has been authorized.")
    elif not user and ev.is_private:
        await ev.reply("Not Found.")
    elif user:
        await ev.reply("User has been authorized.")
        add_auth(user.id)


@hnd(pattern="addauth")
@master_only
async def addauth_cmd(ev):
    await ev.reply("Authorization is not implemented yet.")


@hnd(pattern="delauth")
@master_only
async def delauth_cmd(ev):
    await ev.reply("Authorization is not implemented yet.")


@hnd(pattern="authlist")
@master_only
async def authlist_cmd(ev):
    await ev.reply("Authorization is not implemented yet.")


@hnd(pattern="ev")
@auth_only
async def _eval(e):
    try:
        c = e.text.split(" ", 1)[1]
    except IndexError:
        return await e.reply("No code provided")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        value = await aexec(c, e)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or value or "No output"
    if len(str(evaluation)) > 4094:
        with io.BytesIO(str(evaluation).encode()) as file:
            file.name = "eval.txt"
            return await e.respond(file=file)
    final_output = (
        "__►__ **EVALPy**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            c,
            evaluation,
        )
    )
    await e.reply(final_output)


async def aexec(code, event):
    exec(
        (
            "async def __aexec(e, client): "
            + "\n p = print"
            + "\n message = event = e"
            + "\n r = reply = await event.get_reply_message()"
            + "\n chat = event.chat_id"
            + "\n from pprint import pprint"
            + "\n pp = pprint"
        )
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](event, event.client)


@hnd(pattern="shell")
@auth_only
async def _exec(e):
    try:
        cmd = e.text.split(maxsplit=1)[1]
    except IndexError:
        return await e.reply("No cmd provided.")
    p = await e.reply("Processing...")
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    out = str(stdout.decode().strip()) + str(stderr.decode().strip())
    if len(out) > 4095:
        with io.BytesIO(out.encode()) as file:
            file.name = "exec.txt"
            await e.reply(file=file)
            await p.delete()
    else:
        f = "`BASH` \n`Output:`\n\n```{}```".format(out)
        await p.edit(f)
