#!/bin/bash

OWNER=${1:-$USER}
WORKING_DIR=${2:-$HOME}

echo "### Installing Obscreen Player ###"
echo "# Using user: $USER_ARG"
echo "# Working Directory: $WORKING_DIR"
echo "# ------------------------------ #"

# Update and install necessary packages
apt update
apt install -y xinit xserver-xorg chromium-browser unclutter

# Add user to tty and video groups
usermod -aG tty $OWNER
usermod -aG video $OWNER

# Configure Xwrapper
touch /etc/X11/Xwrapper.config
grep -qxF "allowed_users=anybody" /etc/X11/Xwrapper.config || echo "allowed_users=anybody" | tee -a /etc/X11/Xwrapper.config
grep -qxF "needs_root_rights=yes" /etc/X11/Xwrapper.config || echo "needs_root_rights=yes" | tee -a /etc/X11/Xwrapper.config

# Create the systemd service to start Chromium in kiosk mode
curl https://raw.githubusercontent.com/jr-k/obscreen/master/system/obscreen-player.service  | sed "s#/home/pi#$WORKING_DIR#g" | sed "s#=pi#=$OWNER#g" | tee /etc/systemd/system/obscreen-player.service

# Reload systemd, enable and start the service
systemctl daemon-reload
systemctl enable obscreen-player.service
systemctl set-default graphical.target
systemctl start obscreen-player.service

