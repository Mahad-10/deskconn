#!/bin/sh

echo "
To allow deskconn to run in the background, you need to create a systemd unit,
which ensures that deskconn automatically starts whenever your computer is
restarted.

To do the above, create a file named deskconn.service in
/home/$USER/.config/systemd/user/ (if that directory doesn't exist, create it)
and paste the below config inside it (/home/$USER/.config/systemd/user/deskconn.service)

[Unit]
Description=Deskconn session service

[Service]
ExecStart=/snap/bin/deskconn.session

[Install]
WantedBy=default.target


Then run below commands to enable that service

systemctl --user enable deskconn.service
systemctl --user start deskconn.service
"
