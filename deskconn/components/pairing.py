import binascii
import os
import random
from pathlib import Path
import tempfile

from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp
from nacl.public import PrivateKey
from sqlitedict import SqliteDict
from twisted.internet import reactor


def add_key(key):
    db_path = os.path.join(os.environ.get("HOME"), "deskconn.sqlite")
    db = SqliteDict(db_path)
    if 'keys' not in db.keys():
        db['keys'] = [key]
    else:
        k = db['keys']
        k.append(key)
        db['keys'] = k
    db.commit()
    db.close()


def has_key(key):
    db_path = os.path.join(os.environ.get("HOME"), "deskconn.sqlite")
    db = SqliteDict(db_path)
    if 'keys' not in db.keys():
        return False
    keys = db.get('keys')
    return key in keys


class PairingComponent(ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self._pending_otps = []
        self._key_file = os.path.join(os.environ.get("HOME"), "deskconn.keys")
        self._public_key = None
        self._private_key = None
        self._generate_and_save_key_pair()

    def _generate_and_save_key_pair(self):
        if os.path.exists(self._key_file):
            with open(self._key_file) as file:
                self._public_key, self._private_key = file.read().split("\n")
        else:
            sk = PrivateKey.generate()
            self._public_key = binascii.b2a_hex(sk.public_key.encode()).decode()
            self._private_key = binascii.b2a_hex(sk.encode()).decode()
            with open(self._key_file, 'w') as file:
                file.write(self._public_key)
                file.write("\n")
                file.write(self._private_key)

    async def onJoin(self, details):
        print(details)
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
            add_key(public_key)
            return self._public_key
        raise wamp.ApplicationError("org.deskconn.errors.invalid_otp")
