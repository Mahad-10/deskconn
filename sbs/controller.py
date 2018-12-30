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
import os
import socket
import time

import dbus
from Xlib import display, X
from Xlib.ext.xtest import fake_input
from zeroconf import ServiceInfo, Zeroconf

from sbs.constants import BRIGHTNESS_CONFIG_FILE, BRIGHTNESS_STEP, BRIGHTNESS_MAX, DBUS_DATA

_PRESSED_KEYS = []
_PRESSED_MOUSE_BUTTONS = []


def validate_and_sanitize_brightness_value(value):
    assert (isinstance(value, int) or isinstance(value, float)), 'brightness must be either int or float'

    if value < 1:
        return 1
    if value > 100:
        return 100
    return value


def percent_to_internal(percent):
    validated = validate_and_sanitize_brightness_value(percent)
    return int((validated / 100) * BRIGHTNESS_MAX)


class BrightnessControl:
    def __init__(self):
        super().__init__()
        self.change_in_progress = False

    @property
    def brightness_current(self):
        with open(BRIGHTNESS_CONFIG_FILE) as config_file:
            return int(config_file.read().strip())

    def write_brightness_value(self, value):
        with open(BRIGHTNESS_CONFIG_FILE, 'w') as config_file:
            config_file.write(str(value))

    def get_current_brightness_percentage(self, current_brightness_raw=0):
        # Calculate brightness percentage from provided "raw" value
        if current_brightness_raw > 0:
            return int((current_brightness_raw / BRIGHTNESS_MAX) * 100)
        # Seems we need to read from the backend
        return int((self.brightness_current / BRIGHTNESS_MAX) * 100)

    def set_brightness(self, percent):
        brightness_requested = percent_to_internal(percent)
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


class Mouse:
    def __init__(self):
        super().__init__()
        self.display = display.Display()
        screen_data = self.display.screen()._data
        self.screen_height = screen_data['height_in_pixels']
        self.screen_width = screen_data['width_in_pixels']

    @property
    def x(self):
        return self.position()[0]

    @property
    def y(self):
        return self.position()[1]

    def _press(self, button=1):
        _PRESSED_MOUSE_BUTTONS.append(button)
        fake_input(self.display, X.ButtonPress, button)
        self.display.sync()

    def _release(self, button=1):
        if button in _PRESSED_MOUSE_BUTTONS:
            _PRESSED_MOUSE_BUTTONS.remove(button)
        fake_input(self.display, X.ButtonRelease, button)
        self.display.sync()

    def click(self, button=1, press_duration=0.10):
        self._press(button)
        time.sleep(press_duration)
        self._release(button)

    def move(self, percent_x, percent_y):
        _, pixels_x = math.modf((percent_x / 100) * self.screen_width)
        _, pixels_y = math.modf((percent_y / 100) * self.screen_height)
        fake_input(self.display, X.MotionNotify, False, x=self.x + (int(pixels_x)), y=self.y + (int(pixels_y)))
        self.display.sync()

    def position(self):
        coord = self.display.screen().root.query_pointer()._data
        return coord["root_x"], coord["root_y"]


def get_local_address():
    # FIXME: depends on the internet, hence breaks the "edge" usecase.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("www.google.com", 80))
    res = s.getsockname()[0]
    s.close()
    return res


class Display:
    def __init__(self):
        self.environment = os.environ.get('XDG_CURRENT_DESKTOP', 'KDE').lower()
        if self.environment not in DBUS_DATA.keys():
            raise RuntimeError('Supported environments: {}'.format(', '.join(DBUS_DATA.keys())))
        os.environ.update({"DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus"})
        os.seteuid(1000)
        bus = dbus.SessionBus()
        os.seteuid(0)
        self.screen_saver = bus.get_object(DBUS_DATA[self.environment]['service_name'],
                                           DBUS_DATA[self.environment]['path'])
        self.iface = dbus.Interface(self.screen_saver, DBUS_DATA[self.environment]['interface'])

    def is_locked(self):
        return getattr(self.iface, DBUS_DATA[self.environment]['methods']['is_locked'])()

    def lock(self):
        if not self.is_locked():
            getattr(self.iface, DBUS_DATA[self.environment]['methods']['lock'])()
        return self.is_locked()


class ServiceDiscovery:
    def __init__(self, type_='_crossbar._tcp', name='Screen brightness server', address='0.0.0.0', port=5020):
        super().__init__()

        self.type_ = type_
        self.info = ServiceInfo(
            type_="{}.local.".format(type_),
            name="{}.{}.local.".format(name, type_),
            address=socket.inet_aton(get_local_address() if address == '0.0.0.0' else address),
            port=port,
            properties={}
        )

        self.zeroconf = Zeroconf()

    def start_publishing(self):
        print("Registering service: {}".format(self.type_))
        self.zeroconf.register_service(self.info)
        print("Registered service: {}".format(self.type_))

    def stop_publishing(self):
        print("Unregistering service: {}".format(self.type_))
        self.zeroconf.unregister_service(self.info)
        print("Unregistered service: {}".format(self.type_))
