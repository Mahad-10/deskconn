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
import time

from autobahn.twisted.component import Component, run
from evdev import uinput, ecodes
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet import reactor

from deskconn.components.brightness import ScreenBrightnessComponent


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
component = Component(transports=[transport], realm="deskconn", session_factory=ScreenBrightnessComponent)


class Slides:
    def __init__(self):
        self.device = uinput.UInput()

    def _press_and_release(self, key):
        self.device.write(ecodes.EV_KEY, key, 1)
        time.sleep(0.1)
        self.device.write(ecodes.EV_KEY, key, 0)
        self.device.syn()

    def next(self):
        self._press_and_release(ecodes.KEY_PAGEDOWN)

    def previous(self):
        self._press_and_release(ecodes.KEY_PAGEUP)

    def start(self):
        self._press_and_release(ecodes.KEY_KEYF5)

    def end(self):
        self._press_and_release(ecodes.KEY_ESC)


@component.on_join
async def joined(session, details):
    session.log.info('realm joined: {}'.format(details.realm))

    slides = Slides()
    await session.register(slides.next, 'org.deskconn.deskconn.slides.next')
    await session.register(slides.previous, 'org.deskconn.deskconn.slides.previous')
    await session.register(slides.end, 'org.deskconn.deskconn.slides.end')


if __name__ == '__main__':
    component._transports[0].max_retries = 0
    run([component])
