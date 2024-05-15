#!/bin/bash

# Disable screensaver and DPMS
xset s off
xset -dpms
xset s noblank

# Start unclutter to hide the mouse cursor
unclutter -display :0 -noevents -grab &

# Modify Chromium preferences to avoid restore messages
mkdir -p /home/pi/.config/chromium/Default 2>/dev/null
touch /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exited_cleanly": false/"exited_cleanly": true/' /home/pi/.config/chromium/Default/Preferences

RESOLUTION=$(DISPLAY=:0 xrandr | grep '*' | awk '{print $1}')
WIDTH=$(echo $RESOLUTION | cut -d 'x' -f 1)
HEIGHT=$(echo $RESOLUTION | cut -d 'x' -f 2)

# Start Chromium in kiosk mode
chromium-browser --disable-features=Translate --ignore-certificate-errors --disable-web-security --disable-restore-session-state --autoplay-policy=no-user-gesture-required --start-maximized --allow-running-insecure-content --remember-cert-error-decisions --noerrdialogs --kiosk --incognito --window-position=0,0 --window-size=${WIDTH},${HEIGHT} --display=:0 http://localhost:5000
