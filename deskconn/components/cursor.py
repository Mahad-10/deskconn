import math
import time

from autobahn.twisted import wamp
from twisted.internet.defer import inlineCallbacks
from Xlib import display, X
from Xlib.ext.xtest import fake_input

_PRESSED_KEYS = []
_PRESSED_MOUSE_BUTTONS = []


class MouseCursor:
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


class MouseServerComponent(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.mouse = MouseCursor()

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('realm joined: {}'.format(details.realm))
        yield self.register(self.mouse.move, 'org.deskconn.mouse.move')

    def onLeave(self, details):
        self.log.info('session left: {}'.format(details))
        self.disconnect()
