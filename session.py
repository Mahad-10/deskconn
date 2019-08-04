#!/usr/bin/python3
#
# Copyright (C) 2018  Omer Akram
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

from autobahn.twisted.component import Component, run
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet import reactor

from deskconn.components.lock_screen import ScreenLockComponent
from deskconn.components.cursor import MouseServerComponent


def _is_snap():
    return os.environ.get('SNAP_NAME') == 'deskconn'


if not _is_snap():
    # Make non-snap environment "feel like home"
    os.environ['SNAP_COMMON'] = os.path.expandvars('$HOME/deskconnd-sock-dir')

transport = {
    "type": "rawsocket",
    "url": "ws://localhost/ws",
    "endpoint": UNIXClientEndpoint(reactor,
                                   os.path.join(os.path.expandvars('$SNAP_COMMON/deskconnd-sock-dir'),
                                                'deskconn.sock')),
    "serializer": "cbor",
}


lock_comp = Component(transports=[transport], realm="deskconn", session_factory=ScreenLockComponent)
mouse_comp = Component(transports=[transport], realm="deskconn", session_factory=MouseServerComponent)


def main():
    run([lock_comp, mouse_comp])


if __name__ == '__main__':
    main()
