from pathlib import Path
import tempfile
import uuid

import requests


if __name__ == '__main__':
    unique_id = str(uuid.uuid4())
    Path("{}/{}".format(tempfile.gettempdir(), unique_id)).touch()
    response = requests.post("http://localhost:5020/call",
                             json={"procedure": "org.deskconn.pairing.generate", "args": [unique_id]})
    if response.status_code == 200:
        data = response.json()
        if "args" in data:
            print("\nYour Pairing OTP is: {}\n".format(data["args"][0]))
