import os

from setuptools import setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='deskconn',
    version='0.1.0',
    packages=['sbs'],
    url='https://github.com/om26er/screen-brightness-server',
    license='GNU GPL Version 3',
    author='Omer Akram',
    author_email='om26er@gmail.com',
    description='Expose your desktop functionalities over network.',
    download_url='https://github.com/deskconn/deskconn-server/tarball/0.1.0',
    keywords=['linux', 'ubuntu'],
    install_requires=['autobahn[twisted,serialization]', 'crossbar', 'twisted', 'txaio', 'zeroconf', 'xlib'],
)
