#
# Copyright (C) 2018-2019  Omer Akram
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

import math
import os
import time

from autobahn import wamp
from twisted.internet import threads

DRIVER_ROOT = '/sys/class/backlight/intel_backlight/'
BRIGHTNESS_CONFIG_FILE = os.path.join(DRIVER_ROOT, 'brightness')
BRIGHTNESS_MAX_REFERENCE_FILE = os.path.join(DRIVER_ROOT, 'max_brightness')
BRIGHTNESS_STEP = 25
BRIGHTNESS_MIN = 1


class BrightnessControl:
    def __init__(self):
        super().__init__()
        with open(BRIGHTNESS_MAX_REFERENCE_FILE) as file:
            self._brightness_max = int(file.read().strip())
        self.change_in_progress = False

    @staticmethod
    def has_backlight():
        return os.path.exists(BRIGHTNESS_MAX_REFERENCE_FILE)

    @property
    def max_brightness(self):
        return self._brightness_max

    @staticmethod
    def validate_and_sanitize_brightness_value(value):
        assert (isinstance(value, int) or isinstance(value, float)),\
            'brightness must be either int or float'

        if value < 1:
            return 1
        if value > 100:
            return 100
        return value

    def percent_to_internal(self, percent):
        validated = self.validate_and_sanitize_brightness_value(percent)
        return int((validated / 100) * self.max_brightness)

    @property
    def brightness_current(self):
        with open(BRIGHTNESS_CONFIG_FILE) as config_file:
            return int(config_file.read().strip())

    @staticmethod
    def write_brightness_value(value):
        with open(BRIGHTNESS_CONFIG_FILE, 'w') as config_file:
            config_file.write(str(value))

    @wamp.register(None)
    async def get(self):
        return int((self.brightness_current / self.max_brightness) * 100)

    @wamp.register(None)
    async def set(self, percent):
        await threads.deferToThread(self._set, percent)

    def _set(self, percent):
        brightness_requested = self.percent_to_internal(percent)
        # Abort any in progress change
        self.change_in_progress = False

        brightness = self.brightness_current

        self.change_in_progress = True
        if brightness_requested > brightness:
            decimal_steps, full_steps = math.modf((brightness_requested - brightness) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                if not self.change_in_progress:
                    break
                brightness += BRIGHTNESS_STEP
                self.write_brightness_value(brightness)
                time.sleep(0.02)
            if self.change_in_progress:
                brightness += int(decimal_steps * BRIGHTNESS_STEP)
                self.write_brightness_value(brightness)
        else:
            decimal_steps, full_steps = math.modf((brightness - brightness_requested) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                if not self.change_in_progress:
                    break
                brightness -= BRIGHTNESS_STEP
                self.write_brightness_value(brightness)
                time.sleep(0.02)
            if self.change_in_progress:
                brightness -= int(decimal_steps * BRIGHTNESS_STEP)
                self.write_brightness_value(brightness)

        # Ensure brightness is correct at the end
        if brightness != brightness_requested:
            self.write_brightness_value(brightness_requested)

        self.change_in_progress = False
