import socket

from autobahn.twisted import wamp
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import threads
from zeroconf import ServiceInfo, Zeroconf


def get_local_address():
    # FIXME: depends on the internet, hence breaks the "edge" usecase.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("www.google.com", 80))
    res = s.getsockname()[0]
    s.close()
    return res


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


class ServiceDiscoveryComponent(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.discovery = ServiceDiscovery()

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))
        res = yield threads.deferToThread(self.discovery.start_publishing)
        returnValue(res)

    def onLeave(self, details):
        self.log.info('session left: {}'.format(details))
        self.discovery.stop_publishing()
        self.disconnect()