import psutil
import platform
import datetime

from modules.helpers import hnd, auth_only, master_only, get_size, format_time


def get_system_statistics():
    return '''
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
            datetime.datetime.now().timestamp() - psutil.boot_time()
        ),
        boot_time=datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@hnd(pattern="sys")
@auth_only
async def sys_cmd(ev):
    await ev.reply(get_system_statistics())


@hnd(pattern="auth")
@master_only
async def auth_cmd(ev):
    await ev.reply("Authorization is not implemented yet.")


@hnd(pattern="addauth")
@master_only
async def addauth_cmd(ev):
    await ev.reply("Authorization is not implemented yet.")


@hnd(pattern="delauth")
@master_only
async def delauth_cmd(ev):
    await ev.reply("Authorization is not implemented yet.")
