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
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet import reactor

from deskconn.components.brightness import ScreenBrightnessComponent


if __name__ == '__main__':
    if os.environ.get("SNAP_NAME") != "deskconn":
        os.environ['SNAP_COMMON'] = os.path.expandvars('$HOME')

    sock_path = os.path.join(os.path.expandvars('$SNAP_COMMON/deskconnd-sock-dir'), 'deskconnd.sock')
    print("finding deskconnd...")
    while not os.path.exists(sock_path):
        time.sleep(1)
    print("found, now connecting.")

    transport = {
        "type": "rawsocket",
        "url": "ws://localhost/ws",
        "endpoint": UNIXClientEndpoint(reactor, sock_path),
        "serializer": "cbor",
    }

    component = Component(transports=[transport], realm="deskconn", session_factory=ScreenBrightnessComponent)
    component._transports[0].max_retries = 0
    run([component])
