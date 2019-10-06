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

import os
import shlex
import subprocess
import time

from autobahn.twisted.component import Component, run
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet import reactor

from deskconn.components.lock_screen import Display


def wait_for_deskconnd():
    if os.environ.get("SNAP_NAME") == "deskconn":
        crossbar = os.path.expandvars("$SNAP_COMMON/crossbar-runtime-dir/bin/crossbar")
        if not os.path.exists(crossbar):
            print("Waiting for crossbar runtime directory interface to connect")
            while not os.path.exists(crossbar):
                time.sleep(1)
        print("Found crossbar runtime environment")
    else:
        os.environ['SNAP_COMMON'] = os.path.expandvars('$HOME')

    sock_path = os.path.join(os.path.expandvars('$SNAP_COMMON/deskconnd-sock-dir'), 'deskconnd.sock')
    print("finding deskconnd...")
    while not os.path.exists(sock_path):
        time.sleep(1)
    print("found, now connecting.")
    return sock_path


transport = {
    "type": "rawsocket",
    "url": "ws://localhost/ws",
    "endpoint": UNIXClientEndpoint(reactor, wait_for_deskconnd()),
    "serializer": "cbor",
}
component = Component(transports=[transport], realm="deskconn")


def open_url(url):
    subprocess.check_call(shlex.split("xdg-open {}".format(url)))


@component.on_join
async def joined(session, details):
    session.log.info('realm joined: {}'.format(details.realm))
    await session.register(open_url, 'org.deskconn.deskconn.url.open')

    display = Display()
    await session.register(display.is_locked, 'org.deskconn.deskconn.display.is_locked')
    await session.register(display.lock, 'org.deskconn.deskconn.display.lock')


if __name__ == '__main__':
    run([component])
