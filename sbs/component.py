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

from autobahn.twisted import wamp
from twisted.internet import inotify
from twisted.python import filepath
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import threads

from sbs.controller import BrightnessControl, percent_to_internal
from sbs.constants import BRIGHTNESS_CONFIG_FILE, BRIGHTNESS_MAX


class BrightnessServerSession(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.controller = BrightnessControl()
        self.notifier = inotify.INotify()

        self._publisher_id = None
        self._requested_value_internal = -1
        self._reset_publisher = False
        self._last_value = -1

    def onConnect(self):
        self.log.info('transport connected')
        self.join(self.config.realm)

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))
        self.notifier.startReading()
        self.notifier.watch(filepath.FilePath(BRIGHTNESS_CONFIG_FILE), callbacks=[self.publish_brightness_changed])

        yield self.register(self.set_brightness, 'io.crossbar.set_brightness')
        yield self.register(self.controller.get_current_brightness_percentage, 'io.crossbar.get_brightness')

    def onLeave(self, details):
        self.log.info('session left: {}'.format(details))
        self.notifier.stopReading()
        self.disconnect()

    @inlineCallbacks
    def set_brightness(self, percentage, publisher_id=None):
        def actually_set_brightness(percent, pub_id):
            self._publisher_id = pub_id
            self._requested_value_internal = percent_to_internal(percent)
            self.controller.set_brightness(percent)

        res = yield threads.deferToThread(actually_set_brightness, percentage, publisher_id)
        returnValue(res)

    def publish_brightness_changed(self, _ignored, file_path, _mask):
        with open(file_path.path) as file:
            current_value = int(file.read().strip())

            # Inotify sometimes notifies duplicate events, we only
            # want to publish a "brightness_changed" when its unique from
            # last "edit".
            if current_value == self._last_value:
                return

            self.publish("io.crossbar.brightness_changed",
                         percentage=int((current_value / BRIGHTNESS_MAX) * 100),
                         publisher_id=self._publisher_id)

            # Reset the "publisher" once brightness is set to the requested
            # level so that any internal change (bright changes using keyboard buttons)
            # doesn't do a publish with false "publisher".
            if current_value == self._requested_value_internal:
                self._publisher_id = None

            self._last_value = current_value
