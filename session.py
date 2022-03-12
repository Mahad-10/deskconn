#!/usr/bin/env python3
#
# Copyright (c) CODEBASE
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import shlex
import subprocess

from autobahn.twisted.component import run

from deskconn.common import wait_for_deskconnd, get_component, PREFIX
from deskconn.components.lock_screen import Display
from deskconn.components.slides import Slides
from deskconn.components.url import open_

component = get_component()


def notify(message, app=None):
    subprocess.check_call(shlex.split("notify-send -a {} {}".format(app, message)))


@component.on_join
async def joined(session, details):
    session.log.info('session joined: {}'.format(details.realm))
    await session.register(open_, 'open', prefix=PREFIX.format(component="url"))
    await session.register(Display(), prefix=PREFIX.format(component="display"))
    await session.register(notify, 'notify', prefix=PREFIX.format(component="notify"))
    await session.register(Slides(), prefix=PREFIX.format(component="slides"))


if __name__ == '__main__':
    wait_for_deskconnd()
    run([component])
