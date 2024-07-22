#!/bin/bash

OWNER=${1:-$USER}
WORKING_DIR=${2:-$HOME}

echo "# ==============================="
echo "# Installing Obscreen Studio"
echo "# Using user: $OWNER"
echo "# Working Directory: $WORKING_DIR"
echo "# ==============================="

# ============================================================
# Installation
# ============================================================

echo ""
echo "# Waiting 3 seconds before installation..."
sleep 3

# Install system dependencies
sudo apt-get update
sudo apt-get install -y git python3-pip python3-venv libsqlite3-dev ntfs-3g ffmpeg

# Get files
cd $WORKING_DIR
git clone https://github.com/jr-k/obscreen.git
cd obscreen
chown -R pi:pi ./

# Install application dependencies
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt

# Customize server default values
cp .env.dist .env

# Add user to needed group
usermod -aG plugdev $OWNER

# ============================================================
# Automount script for external storage
# ============================================================

curl https://raw.githubusercontent.com/jr-k/obscreen/master/system/external-storage/10-obscreen-media-automount.rules  | sed "s#/home/pi#$WORKING_DIR#g" | tee /etc/udev/rules.d/10-obscreen-media-automount.rules
udevadm control --reload-rules
systemctl restart udev
udevadm trigger

# ============================================================
# Systemd service installation
# ============================================================

cat "./system/obscreen-studio.service" | sed "s#/home/pi#$WORKING_DIR#g" | sed "s#=pi#=$OWNER#g" | sudo tee /etc/systemd/system/obscreen-studio.service
sudo systemctl daemon-reload
sudo systemctl enable obscreen-studio.service

# ============================================================
# Start
# ============================================================

sudo systemctl restart obscreen-studio.service
