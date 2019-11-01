import shlex
import subprocess


def open_(url):
    subprocess.check_call(shlex.split("xdg-open {}".format(url)))
