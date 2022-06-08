import psutil
import platform
import datetime

from modules.helpers import hnd, auth_only, master_only, get_size, format_time
import io
import sys
import asyncio
import traceback
from .db import add_auth


def get_system_statistics():
    STATS = '''
    **System statistics:**
    **OS:** {os}
    **CPU Cores:** {cpu}
    **CPU usage:** {cpu_usage}%
    **RAM:** {ram}
    **RAM usage:** {ram_usage}%

    **Disk:** {disk}
    **Disk usage:** {disk_usage}
    **Disk Free:** {disk_free}

    **Network sent:** {network_sent}
    **Network received:** {network_received}

    **Uptime:** {uptime}
    **Boot time:** {boot_time}
    **Time:** {time}
    '''.format(
        os=platform.system(),
        cpu=psutil.cpu_count(),
        cpu_usage=psutil.cpu_percent(),
        ram=get_size(psutil.virtual_memory().total),
        ram_usage=psutil.virtual_memory().percent,
        disk=get_size(psutil.disk_usage("/").total),
        disk_usage=get_size(psutil.disk_usage("/").used),
        disk_free=get_size(psutil.disk_usage("/").free),
        network=get_size(psutil.net_io_counters().bytes_sent),
        network_usage=get_size(psutil.net_io_counters().bytes_sent),
        network_sent=get_size(psutil.net_io_counters().bytes_sent),
        network_received=get_size(psutil.net_io_counters().bytes_recv),
        uptime=format_time(
            datetime.datetime.now().timestamp() - psutil.boot_time()),
        boot_time=datetime.datetime.fromtimestamp(
            psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return STATS


@hnd(pattern="sys")
@auth_only
async def sys_cmd(ev):
    await ev.reply(get_system_statistics())


@hnd(pattern="auth")
@master_only
async def auth_cmd(ev):
    await ev.reply("Authed this chat.")
    add_auth(ev.chat_id)


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
