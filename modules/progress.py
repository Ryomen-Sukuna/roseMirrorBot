async def progress_edit(current, total, speed, eta, filename, event):
    await event.edit(f"Downloading file: {filename} | {current}/{total} | {speed} | {eta}")
