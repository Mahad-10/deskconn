import binascii
import os
import random
from pathlib import Path
import tempfile

from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp
from nacl.public import PrivateKey
from twisted.internet import reactor


class PairingComponent(ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self._pending_otps = []
        self.key_file = os.path.join(os.environ.get("HOME"), "deskconn.keys")
        self._public_key = None
        self._private_key = None
        self.generate_and_save_key_pair()

    def generate_and_save_key_pair(self):
        if os.path.exists(self.key_file):
            with open(self.key_file) as file:
                self._public_key, self._private_key = file.read().split("\n")
        else:
            sk = PrivateKey.generate()
            self._public_key = binascii.b2a_hex(sk.public_key.encode()).decode()
            self._private_key = binascii.b2a_hex(sk.encode()).decode()
            with open(self.key_file, 'w') as file:
                file.write(self._public_key)
                file.write("\n")
                file.write(self._private_key)

    async def onJoin(self, details):
        self.log.info('realm joined: {}'.format(details.realm))
        await self.register(self, prefix="org.deskconn.pairing.")

    def _revoke_key(self, key):
        if key in self._pending_otps:
            self._pending_otps.remove(key)

    @wamp.register(None)
    async def generate(self, local_identity_token):
        token_path = os.path.join(tempfile.gettempdir(), local_identity_token)
        if os.path.exists(token_path):
            Path(token_path).unlink()
            key = random.randint(100000, 999999)
            self._pending_otps.append(key)
            reactor.callLater(30, self._revoke_key, key)
            return key
        raise wamp.ApplicationError("org.deskconn.errors.invalid_caller")

    @wamp.register(None)
    async def pair(self, otp, public_key):
        assert otp.isdigit()
        otp = int(otp.strip())
        if otp in self._pending_otps:
            self._pending_otps.remove(otp)
            print("Saving public key...", public_key)
            return self._public_key
        raise wamp.ApplicationError("org.deskconn.errors.invalid_otp")
