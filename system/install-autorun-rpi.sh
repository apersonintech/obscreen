#!/bin/bash

# Update and install necessary packages
apt update
apt install -y xinit xserver-xorg chromium-browser unclutter

# Add user pi to tty and video groups
usermod -aG tty pi
usermod -aG video pi

# Configure Xwrapper
touch /etc/X11/Xwrapper.config
grep -qxF "allowed_users=anybody" /etc/X11/Xwrapper.config || echo "allowed_users=anybody" | tee -a /etc/X11/Xwrapper.config
grep -qxF "needs_root_rights=yes" /etc/X11/Xwrapper.config || echo "needs_root_rights=yes" | tee -a /etc/X11/Xwrapper.config

# Create the systemd service to start Chromium in kiosk mode
curl https://raw.githubusercontent.com/jr-k/obscreen/master/system/obscreen-player.service | tee /etc/systemd/system/obscreen-player.service

# Reload systemd, enable and start the service
systemctl daemon-reload
systemctl enable obscreen-player.service
systemctl set-default graphical.target
systemctl start obscreen-player.service

