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

from autobahn.twisted.wamp import ApplicationRunner

from deskconn.components.lock_screen import ScreenLockComponent
from deskconn.components.cursor import MouseServerComponent


def main():
    runner = ApplicationRunner("ws://127.0.0.1:5020/ws", "deskconn")
    runner.run(MouseServerComponent, start_reactor=False)
    runner.run(ScreenLockComponent)


if __name__ == '__main__':
    main()
