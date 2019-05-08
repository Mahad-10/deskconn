import os
import shlex
import signal
import subprocess
import uuid

from autobahn.twisted import wamp

SERVICE_DATA = """
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">

<service-group>
  <name replace-wildcards="yes">%h</name>
  <service>
    <type>_deskconn._tcp</type>
    <port>5020</port>
    <txt-record>realm=deskconn</txt-record>
  </service>
</service-group>
"""


class ServiceDiscoveryComponent(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.process = None

    @property
    def command(self):
        return "avahi-publish -s deskconn-{} _deskconn._tcp 5020 realm=deskconn".format(str(uuid.uuid4()))

    @staticmethod
    def is_ubuntu_core():
        with open("/proc/cmdline") as f:
            return 'snap_core' in f.read()

    def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))
        if self.is_ubuntu_core():
            service_dir = '$SNAP_COMMON/etc/avahi/services'
            service_file = os.path.join(os.path.expandvars(service_dir), 'deskconn.service')
            if os.path.exists(service_dir) and not os.path.exists(service_file):
                with open(service_file) as file:
                    file.write(SERVICE_DATA)
        else:
            self.process = subprocess.Popen(shlex.split(self.command))

    def onLeave(self, details):
        if self.process:
            self.process.send_signal(signal.SIGINT)
