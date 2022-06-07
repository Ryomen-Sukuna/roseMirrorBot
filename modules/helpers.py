import functools
from subprocess import Popen, PIPE
from config import bot


def run_shell(command: str, wait: bool):
    subproc = Popen(command, stdout=PIPE, stderr=PIPE,
                    shell=True, universal_newlines=True)
    if wait:
        stdout, stderr = subproc.communicate()
        return stdout, stderr
    else:
        return subproc

    