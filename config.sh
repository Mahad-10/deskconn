#!/bin/sh

echo "
To allow deskconn to run in the background, you need to create a systemd unit,
which ensures that deskconn automatically starts whenever your computer is
restarted. To do that, just copy the following text, and run it in a terminal.


mkdir -p /home/$USER/.config/systemd/user/
echo '[Unit]
Description=Deskconn session service
[Service]
ExecStart=/snap/bin/deskconn.session
[Install]
WantedBy=default.target' > /home/$USER/.config/systemd/user/deskconn.service"
echo "
systemctl --user enable deskconn.service
systemctl --user start deskconn.service
"
