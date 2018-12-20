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

import math
import time

from sbs.constants import BRIGHTNESS_CONFIG_FILE, BRIGHTNESS_STEP, BRIGHTNESS_MAX


def validate_and_sanitize_brightness_value(value):
    assert (isinstance(value, int) or isinstance(value, float)), 'brightness must be either int or float'

    if value < 1:
        return 1
    if value > 100:
        return 100
    return value


class BrightnessControl:
    def __init__(self, component):
        super().__init__()
        assert component is not None, "component must not be none"
        self.component = component
        self.change_in_progress = False

    @property
    def brightness_current(self):
        with open(BRIGHTNESS_CONFIG_FILE) as config_file:
            return int(config_file.read().strip())

    def write_brightness_value(self, value, publish=True):
        with open(BRIGHTNESS_CONFIG_FILE, 'w') as config_file:
            config_file.write(str(value))
            # Publish brightness changes
            if publish and self.component.is_connected():
                self.component.publish("io.crossbar.brightness_changed", self.get_current_brightness_percentage(value))

    def get_current_brightness_percentage(self, current_brightness_raw=0):
        # Calculate brightness percentage from provided "raw" value
        if current_brightness_raw > 0:
            return int((current_brightness_raw / BRIGHTNESS_MAX) * 100)
        # Seems we need to read from the backend
        return int((self.brightness_current / BRIGHTNESS_MAX) * 100)

    def set_brightness(self, percent, publish=True):
        percent = validate_and_sanitize_brightness_value(percent)
        # Abort any in progress change
        self.change_in_progress = False

        brightness_requested = (percent / 100) * BRIGHTNESS_MAX
        brightness = self.brightness_current

        self.change_in_progress = True
        if brightness_requested > brightness:
            decimal_steps, full_steps = math.modf((brightness_requested - brightness) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                if not self.change_in_progress:
                    break
                brightness += BRIGHTNESS_STEP
                self.write_brightness_value(brightness, publish)
                time.sleep(0.02)
            if self.change_in_progress:
                brightness += int(decimal_steps * BRIGHTNESS_STEP)
                self.write_brightness_value(brightness, publish)
        else:
            decimal_steps, full_steps = math.modf((brightness - brightness_requested) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                if not self.change_in_progress:
                    break
                brightness -= BRIGHTNESS_STEP
                self.write_brightness_value(brightness, publish)
                time.sleep(0.02)
            if self.change_in_progress:
                brightness -= int(decimal_steps * BRIGHTNESS_STEP)
                self.write_brightness_value(brightness, publish)
        self.change_in_progress = False
