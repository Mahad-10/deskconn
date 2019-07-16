import os
from pathlib import Path

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
        self.service_file = os.path.join(os.path.expandvars('$SNAP_COMMON'), 'deskconn.service')

    async def onJoin(self, details):
        with open(self.service_file) as file:
            file.write(SERVICE_DATA)

    def onLeave(self, details):
        if os.path.exists(self.service_file):
            Path(self.service_file).unlink()
