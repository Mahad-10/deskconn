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
import shlex
import subprocess
import time

from flask import Flask, request

DRIVER_ROOT = '/sys/class/backlight/intel_backlight/'
BRIGHTNESS_CONFIG_FILE = os.path.join(DRIVER_ROOT, 'brightness')
BRIGHTNESS_MAX_REFERENCE_FILE = os.path.join(DRIVER_ROOT, 'max_brightness')
BRIGHTNESS_STEP = 5
BRIGHTNESS_MIN = 1

app = Flask(__name__)


def run(command):
    return subprocess.check_output(shlex.split(command), universal_newlines=True).strip()


def set_brightness(percent):
    brightness_max = int(run('cat {}'.format(BRIGHTNESS_MAX_REFERENCE_FILE)))
    brightness_current = int(run('cat {}'.format(BRIGHTNESS_CONFIG_FILE)))
    brightness_requested = int((percent / 100) * brightness_max)

    if brightness_requested == brightness_current:
        return

    brightness = brightness_current
    if brightness_requested > brightness_current:
        while brightness <= brightness_max and brightness <= brightness_requested:
            os.system('echo {} > {}'.format(brightness, BRIGHTNESS_CONFIG_FILE))
            brightness += BRIGHTNESS_STEP
            time.sleep(0.01)
    else:
        while brightness > BRIGHTNESS_MIN and brightness >= brightness_requested:
            os.system('echo {} > {}'.format(brightness, BRIGHTNESS_CONFIG_FILE))
            brightness -= BRIGHTNESS_STEP
            time.sleep(0.01)


@app.route('/brightness', methods=['POST'])
def parse_request():
    if 'brightness' not in request.json:
        return 'Invalid request, must include brightness value', 400

    set_brightness(int(request.json['brightness']))
    return 'DONE', 200


if __name__ == '__main__':
    if os.geteuid() != 0:
        print('Must run as root.')
        exit(1)

    app.run(debug=False, host='127.0.0.1', port=5020)

