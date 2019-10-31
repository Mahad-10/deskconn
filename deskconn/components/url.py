import shlex
import subprocess


def open(url):
    subprocess.check_call(shlex.split("xdg-open {}".format(url)))
