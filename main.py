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

