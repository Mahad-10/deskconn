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

from autobahn.asyncio import component

from sbs.controller import BrightnessControl


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
async def register_procedures(session, details):
    controller = BrightnessControl(session)

    reg = await session.register(controller.set_brightness, 'io.crossbar.set_brightness')
    print("registered '{}'".format(reg.procedure))

    reg2 = await session.register(controller.get_current_brightness_percentage, 'io.crossbar.get_brightness')
    print("registered '{}'".format(reg2.procedure))
