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

import asyncio

import aionotify
from autobahn.asyncio import component

from sbs.controller import BrightnessControl
from sbs.constants import BRIGHTNESS_CONFIG_FILE, BRIGHTNESS_MAX

watcher = None
publish_change = True

brightness_component = component.Component(
    transports=[
        {
            "type": "websocket",
            "url": "ws://localhost:5020/ws",
            "endpoint": {
                "type": "tcp",
                "host": "localhost",
                "port": 5020
            }
        }
    ],
    realm="realm1",
)


@brightness_component.on_join
async def register_procedures(session, _details):
    controller = BrightnessControl()

    def set_brightness(percentage, publish=True):
        global publish_change
        publish_change = publish
        controller.set_brightness(percentage)

    reg = await session.register(set_brightness, 'io.crossbar.set_brightness')
    print("registered '{}'".format(reg.procedure))

    reg2 = await session.register(controller.get_current_brightness_percentage, 'io.crossbar.get_brightness')
    print("registered '{}'".format(reg2.procedure))


@brightness_component.on_join
async def enable_watch(session, _details):
    global watcher
    watcher = aionotify.Watcher()
    await watcher.setup(asyncio.get_event_loop())
    watcher.watch(BRIGHTNESS_CONFIG_FILE, flags=aionotify.Flags.MODIFY, alias='brightness_change')
    while not watcher.closed:
        await watcher.get_event()
        global publish_change
        if not publish_change:
            publish_change = True
            continue
        with open(BRIGHTNESS_CONFIG_FILE) as file:
            session.publish("io.crossbar.brightness_changed", (int(file.read().strip()) / BRIGHTNESS_MAX) * 100)


@brightness_component.on_leave
async def cleanup(_session, _details):
    global watcher
    if watcher and not watcher.closed:
        watcher.close()
