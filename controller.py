import math
import os
import time

DRIVER_ROOT = '/sys/class/backlight/intel_backlight/'
BRIGHTNESS_CONFIG_FILE = os.path.join(DRIVER_ROOT, 'brightness')
BRIGHTNESS_MAX_REFERENCE_FILE = os.path.join(DRIVER_ROOT, 'max_brightness')
BRIGHTNESS_STEP = 5
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
    def __init__(self):
        super().__init__()
        self.change_in_progress = False

    @property
    def brightness_current(self):
        return read_brightness_value()

    @property
    def brightness_current_percent(self):
        return float("{:.2f}".format((self.brightness_current / BRIGHTNESS_MAX) * 100))

    def set_brightness(self, percent):
        while self.change_in_progress:
            time.sleep(0.1)

        brightness_requested = (percent / 100) * BRIGHTNESS_MAX
        brightness = self.brightness_current

        self.change_in_progress = True
        if brightness_requested > brightness:
            decimal_steps, full_steps = math.modf((brightness_requested - brightness) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                brightness += BRIGHTNESS_STEP
                write_brightness_value(brightness)
                time.sleep(0.01)
            brightness += int(decimal_steps * BRIGHTNESS_STEP)
            write_brightness_value(brightness)
        else:
            decimal_steps, full_steps = math.modf((brightness - brightness_requested) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                brightness -= BRIGHTNESS_STEP
                write_brightness_value(brightness)
                time.sleep(0.01)
            brightness -= int(decimal_steps * BRIGHTNESS_STEP)
            write_brightness_value(brightness)
        self.change_in_progress = False
