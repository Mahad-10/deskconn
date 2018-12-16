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

from autobahn.asyncio import wamp

import controller


def validate_and_sanitize_data(value):
    assert (isinstance(value, int) or isinstance(value, float)), 'brightness must be either int or float'

    if value < 1:
        return 1
    if value > 100:
        return 100
    return value


class Component(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.controller = controller.BrightnessControl(self)

    async def onJoin(self, details):
        def set_brightness(value):
            self.controller.set_brightness(validate_and_sanitize_data(value))
            self.publish("io.crossbar.brightness_changed", value)

        reg = await self.register(set_brightness, 'io.crossbar.set_brightness')
        print("registered '{}' with id {}".format(reg.procedure, reg.id))

        reg2 = await self.register(self.controller.get_current_brightness_percentage, 'io.crossbar.get_brightness')
        print("registered '{}' with id {}".format(reg2.procedure, reg2.id))


if __name__ == '__main__':
    if os.geteuid() != 0:
        print('Must run as root.')
        exit(1)

    runner = wamp.ApplicationRunner(os.environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:5020/ws"), "realm1")
    runner.run(Component)
