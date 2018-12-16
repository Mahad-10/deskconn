import math
import os
import time

DRIVER_ROOT = '/sys/class/backlight/intel_backlight/'
BRIGHTNESS_CONFIG_FILE = os.path.join(DRIVER_ROOT, 'brightness')
BRIGHTNESS_MAX_REFERENCE_FILE = os.path.join(DRIVER_ROOT, 'max_brightness')
BRIGHTNESS_STEP = 25
BRIGHTNESS_MIN = 1
with open(BRIGHTNESS_MAX_REFERENCE_FILE) as file:
    BRIGHTNESS_MAX = int(file.read().strip())


def write_brightness_value(value):
    with open(BRIGHTNESS_CONFIG_FILE, 'w') as config_file:
        config_file.write(str(value))


def read_brightness_value():
    with open(BRIGHTNESS_CONFIG_FILE) as config_file:
        return int(config_file.read().strip())


class BrightnessControl:
    def __init__(self, component=None):
        super().__init__()
        self.component = component
        self.change_in_progress = False

    @property
    def brightness_current(self):
        return read_brightness_value()

    def get_current_brightness_percentage(self):
        return int((self.brightness_current / BRIGHTNESS_MAX) * 100)

    def abort(self):
        self.change_in_progress = False

    def set_brightness(self, percent):
        self.abort()

        brightness_requested = (percent / 100) * BRIGHTNESS_MAX
        brightness = self.brightness_current

        self.change_in_progress = True
        if brightness_requested > brightness:
            decimal_steps, full_steps = math.modf((brightness_requested - brightness) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                if not self.change_in_progress:
                    break
                brightness += BRIGHTNESS_STEP
                write_brightness_value(brightness)
                time.sleep(0.02)
            if self.change_in_progress:
                brightness += int(decimal_steps * BRIGHTNESS_STEP)
                write_brightness_value(brightness)
        else:
            decimal_steps, full_steps = math.modf((brightness - brightness_requested) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                if not self.change_in_progress:
                    break
                brightness -= BRIGHTNESS_STEP
                write_brightness_value(brightness)
                time.sleep(0.02)
            if self.change_in_progress:
                brightness -= int(decimal_steps * BRIGHTNESS_STEP)
                write_brightness_value(brightness)
        self.change_in_progress = False
