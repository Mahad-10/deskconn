import shlex
import signal
import subprocess
import uuid

from autobahn.twisted import wamp


class ServiceDiscoveryComponent(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.process = None

    @property
    def command(self):
        return "avahi-publish -s deskconn-{} _deskconn._tcp 5020 realm=deskconn".format(str(uuid.uuid4()))

    def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))
        self.process = subprocess.Popen(shlex.split(self.command))

    def onLeave(self, details):
        self.process.send_signal(signal.SIGINT)
