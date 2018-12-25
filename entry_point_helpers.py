import os
import socket


def is_snap():
    return 'screen-brightness-server' in os.environ.get('SNAP', '')


def get_cbdir():
    return os.environ.get('SNAP_USER_DATA') if is_snap() else 'crossbar-config'


def get_local_address():
    # FIXME: depends on the internet, hence breaks the "edge" usecase.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("www.google.com", 80))
    res = s.getsockname()[0]
    s.close()
    return res


def get_start_params():
    params = ['start', '--cbdir', get_cbdir()]
    if is_snap():
        params.append('--config')
        params.append(os.path.join(os.environ.get('SNAP'), 'crossbar-config/config.json'))
    return params
