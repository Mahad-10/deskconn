#!/usr/bin/env python3
#
# Copyright (C) 2018-2019 Omer Akram
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import shlex
import subprocess

from autobahn.twisted.component import run

from deskconn.common import wait_for_deskconnd, get_component, PREFIX
from deskconn.components.lock_screen import Display
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


if __name__ == '__main__':
    wait_for_deskconnd()
    run([component])
