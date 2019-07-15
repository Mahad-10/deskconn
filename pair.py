from autobahn.twisted.component import Component, run

from pathlib import Path
import tempfile
import uuid

comp = Component(transports="ws://localhost:5020/ws", realm="pairing")


@comp.on_join
async def joined(session, _details):
    unique_id = str(uuid.uuid4())
    Path("{}/{}".format(tempfile.gettempdir(), unique_id)).touch()
    res = await session.call("org.deskconn.pairing.generate", unique_id)
    print("\nYour Pairing OTP is: {}\n".format(res))
    session.leave()


if __name__ == '__main__':
    run([comp], None)
