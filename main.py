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
import time

from flask import Flask, request, jsonify

DRIVER_ROOT = '/sys/class/backlight/intel_backlight/'
BRIGHTNESS_CONFIG_FILE = os.path.join(DRIVER_ROOT, 'brightness')
BRIGHTNESS_MAX_REFERENCE_FILE = os.path.join(DRIVER_ROOT, 'max_brightness')
BRIGHTNESS_STEP = 5
BRIGHTNESS_MIN = 1
with open(BRIGHTNESS_MAX_REFERENCE_FILE) as file:
    BRIGHTNESS_MAX = int(file.read().strip())

app = Flask(__name__)


class BrightnessControl:
    def __init__(self):
        super().__init__()
        self.change_in_progress = False

    @property
    def brightness_current(self):
        with open(BRIGHTNESS_CONFIG_FILE) as file:
            return int(file.read().strip())

    @property
    def brightness_current_percent(self):
        return int((self.brightness_current / BRIGHTNESS_MAX) * 100)

    def write_brightness_value(self, value):
        with open(BRIGHTNESS_CONFIG_FILE, 'w') as file:
            file.write(str(value))

    def set_brightness(self, percent):
        while self.change_in_progress:
            time.sleep(0.01)

        brightness_requested = int((percent / 100) * BRIGHTNESS_MAX)
        if brightness_requested == self.brightness_current:
            return

        brightness = self.brightness_current
        if brightness_requested > self.brightness_current:
            self.change_in_progress = True
            while self.change_in_progress and brightness <= BRIGHTNESS_MAX and brightness <= brightness_requested:
                self.write_brightness_value(brightness)
                brightness += BRIGHTNESS_STEP
                time.sleep(0.01)
        else:
            self.change_in_progress = True
            while self.change_in_progress and brightness >= BRIGHTNESS_MIN and brightness >= brightness_requested:
                self.write_brightness_value(brightness)
                brightness -= BRIGHTNESS_STEP
                time.sleep(0.01)

        self.change_in_progress = False


@app.route('/brightness', methods=['GET', 'POST'])
def parse_request():
    if request.method == 'POST':
        if 'brightness' not in request.json:
            return 'Invalid request, must include brightness value', 400
        controller.set_brightness(int(request.json['brightness']))
        return jsonify({'status': 'done'})
    elif request.method == 'GET':
        return jsonify({'brightness': controller.brightness_current_percent})


if __name__ == '__main__':
    if os.geteuid() != 0:
        print('Must run as root.')
        exit(1)

    controller = BrightnessControl()
    app.run(debug=False, host='127.0.0.1', port=5020)

