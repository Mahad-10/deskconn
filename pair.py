import os
from pathlib import Path
import tempfile
import uuid

from autobahn.twisted.component import Component, run

comp = Component(transports="ws://localhost:5020/ws", realm="deskconn")


@comp.on_join
async def joined(session, _details):
    unique_id = str(uuid.uuid4())
    verify_path = os.path.join(tempfile.gettempdir(), unique_id)
    Path(verify_path).touch()
    if os.path.exists(verify_path):
        res = await session.call("org.deskconn.pairing.generate", unique_id)
        print("\nYour Pairing OTP is: {}\n".format(res))
    else:
        print("\nNot able to create {}\n".format(verify_path))
    session.leave()


if __name__ == '__main__':
    run([comp], None)
