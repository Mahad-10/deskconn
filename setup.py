from setuptools import setup

VERSION = '0.9.0'

setup(
    name='deskconn',
    version=VERSION,
    packages=['deskconn', 'deskconn.components'],
    url='https://github.com/deskconn/deskconn',
    license='GNU GPL Version 3',
    author='Omer Akram',
    author_email='om26er@gmail.com',
    description='Expose your desktop functionality over the network.',
    download_url='https://github.com/deskconn/deskconn/tarball/{}'.format(VERSION),
    keywords=['linux', 'ubuntu'],
    install_requires=['dbus-python', 'xlib', 'evdev']
)
