Simple HTTP server to control screen brightness on a Linux laptop

# Installation

The simplest way is to install from snap store.
```bash
$ sudo snap install screen-brightness-server --edge --devmode
```

If you don't want to use the snap package:
Clone the project, install requirements with pip
and create a systemd job to run automatically on boot.

To install requirements, do:
`$ pip3 install -r requirements.txt`

To create a systemd job, run below command and paste the configuration below into it.

```
$ sudo vim /etc/systemd/system/screen-brightness-server.service
```

```bash
[Unit]
Description=Screen Brightness Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=directory_where_you_cloned
ExecStart=./start-crossbar

[Install]
WantedBy=multi-user.target
```

To enable and start the service run:
```bash
sudo systemctl enable screen-brightness-server
sudo systemctl start screen-brightness-server
```

May want to check the status of the server
```bash
systemctl status screen-brightness-server
```
