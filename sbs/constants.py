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

DRIVER_ROOT = '/sys/class/backlight/intel_backlight/'
BRIGHTNESS_CONFIG_FILE = os.path.join(DRIVER_ROOT, 'brightness')
BRIGHTNESS_MAX_REFERENCE_FILE = os.path.join(DRIVER_ROOT, 'max_brightness')
BRIGHTNESS_STEP = 25
BRIGHTNESS_MIN = 1
if os.path.exists(BRIGHTNESS_MAX_REFERENCE_FILE):
    with open(BRIGHTNESS_MAX_REFERENCE_FILE) as file:
        BRIGHTNESS_MAX = int(file.read().strip())
else:
    BRIGHTNESS_MAX = -1
