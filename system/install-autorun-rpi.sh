#!/bin/bash

OWNER=${1:-$USER}
WORKING_DIR=${2:-$HOME}

echo "# ==============================="
echo "# Installing Obscreen Player"
echo "# Using user: $OWNER"
echo "# Working Directory: $WORKING_DIR"
echo "# ==============================="

# ============================================================
# User Interaction
# ============================================================

default_studio_url="http://localhost:5000"
obscreen_studio_url=$default_studio_url
disable_interaction=false

for arg in "$@"
do
    if [ "$arg" == "--disable-interaction" ]; then
        disable_interaction=true
        break
    fi
done

if [ "$disable_interaction" = false ]; then
    if [ -t 0 ]; then
        echo ""
        read -p "Enter Obscreen studio instance URL [${default_studio_url}]: " user_url
        obscreen_studio_url=${user_url:-$default_studio_url}
        read -p "Do you confirm ${obscreen_studio_url} is a valid Obscreen studio instance? [Y/n]: " confirm
        if [[ $confirm == "Y" || $confirm == "y" || $confirm == "" ]]; then
            echo ""
            echo "Using Obscreen studio instance URL: $obscreen_studio_url"
        else
            echo "Confirmation not received. Please run the script again and enter a valid URL."
            exit 1
        fi
    else
        echo "Interactive input required, but not available. Please run the script in an interactive terminal."
        exit 1
    fi
else
    # If --disable-interaction is passed, use the default URL without prompting
    echo ""
    echo "Using Obscreen studio instance URL: $default_studio_url"
fi

# ============================================================
# Installation
# ============================================================


echo ""
echo "# Waiting 3 seconds before installation..."
sleep 3

# Update and install necessary packages
apt update
apt install -y xinit xserver-xorg chromium-browser unclutter pulseaudio

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

# ============================================================
# Autorun script
# ============================================================

mkdir -p "$WORKING_DIR/obscreen/var/run"
curl https://raw.githubusercontent.com/jr-k/obscreen/master/system/autostart-browser-x11.sh  | sed "s#/home/pi#$WORKING_DIR#g" | sed "s#=pi#=$OWNER#g" | sed "s#http://localhost:5000#$obscreen_studio_url#g" | tee "$WORKING_DIR/obscreen/var/run/play"
chmod +x "$WORKING_DIR/obscreen/var/run/play"

# ============================================================
# Start
# ============================================================

# Finally, start player service
systemctl start obscreen-player.service
