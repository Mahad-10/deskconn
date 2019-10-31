import time

from autobahn import wamp
from evdev import uinput, ecodes


class Slides:
    def __init__(self):
        self.device = uinput.UInput()

    def _press_and_release(self, key):
        self.device.write(ecodes.EV_KEY, key, 1)
        time.sleep(0.1)
        self.device.write(ecodes.EV_KEY, key, 0)
        self.device.syn()

    @wamp.register(None)
    def next(self):
        self._press_and_release(ecodes.KEY_PAGEDOWN)

    @wamp.register(None)
    def previous(self):
        self._press_and_release(ecodes.KEY_PAGEUP)

    @wamp.register(None)
    def start(self):
        self._press_and_release(ecodes.KEY_F5)

    @wamp.register(None)
    def end(self):
        self._press_and_release(ecodes.KEY_ESC)
