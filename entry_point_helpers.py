import os


def is_snap():
    return 'screen-brightness-server' in os.environ.get('SNAP', '')


def get_cbdir():
    return os.environ.get('SNAP_USER_DATA') if is_snap() else 'crossbar-config'
