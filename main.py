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

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import time

DRIVER_ROOT = '/sys/class/backlight/intel_backlight/'
BRIGHTNESS_CONFIG_FILE = os.path.join(DRIVER_ROOT, 'brightness')
BRIGHTNESS_MAX_REFERENCE_FILE = os.path.join(DRIVER_ROOT, 'max_brightness')
BRIGHTNESS_STEP = 5
BRIGHTNESS_MIN = 1
with open(BRIGHTNESS_MAX_REFERENCE_FILE) as file:
    BRIGHTNESS_MAX = int(file.read().strip())
BRIGHTNESS_ENDPOINT = "/brightness"


def write_brightness_value(value):
    with open(BRIGHTNESS_CONFIG_FILE, 'w') as config_file:
        config_file.write(str(value))


def read_brightness_value():
    with open(BRIGHTNESS_CONFIG_FILE) as config_file:
        return int(config_file.read().strip())


class BrightnessControl:
    def __init__(self):
        super().__init__()
        self.change_in_progress = False

    @property
    def brightness_current(self):
        return read_brightness_value()

    @property
    def brightness_current_percent(self):
        return int((self.brightness_current / BRIGHTNESS_MAX) * 100)

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
                write_brightness_value(brightness)
                brightness += BRIGHTNESS_STEP
                time.sleep(0.01)
        else:
            self.change_in_progress = True
            while self.change_in_progress and brightness >= BRIGHTNESS_MIN and brightness >= brightness_requested:
                write_brightness_value(brightness)
                brightness -= BRIGHTNESS_STEP
                time.sleep(0.01)

        self.change_in_progress = False


class RestHTTPRequestHandler(BaseHTTPRequestHandler):

    def respond(self, data_dict, code):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps(data_dict).encode())

    def get_current_brightness(self):
        self.respond({'brightness': controller.brightness_current_percent}, 200)

    def send_bad_request(self, message):
        self.respond({'message': message}, 400)

    def do_GET(self):
        if self.path == BRIGHTNESS_ENDPOINT:
            self.get_current_brightness()
        else:
            self.send_bad_request("Invalid URL")

    def do_POST(self):
        if self.path != BRIGHTNESS_ENDPOINT:
            self.send_bad_request("Invalid URL")
            return

        content_type = self.headers.get('Content-Type')
        if 'application/json' in content_type:
            content_length = self.headers.get('Content-Length')
            data = self.rfile.read(int(content_length)).decode()
            data = json.loads(data)
            if 'brightness' in data:
                value = int(data.get('brightness'))
                controller.set_brightness(value)
                self.get_current_brightness()
            else:
                self.send_bad_request("brightness parameter missing.")
        else:
            self.send_bad_request("We only support json input")


if __name__ == '__main__':
    if os.geteuid() != 0:
        print('Must run as root.')
        exit(1)

    httpd = HTTPServer(('127.0.0.1', 5020), RestHTTPRequestHandler)
    controller = BrightnessControl()
    while True:
        httpd.handle_request()
