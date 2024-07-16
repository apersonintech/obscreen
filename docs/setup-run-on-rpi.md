# <img src="https://github.com/jr-k/obscreen/blob/master/docs/img/obscreen.png" width="22"> Obscreen - Autorun on RaspberryPi

> #### 👈 [back to readme](/README.md)

#### 🔴 You want to power RaspberryPi and automatically see your slideshow on a screen connected to it and manage your slideshow ? You're in the right place.

---

## 🎛️ Hardware installation

1. Download RaspberryPi Imager and setup an sdcard with `Raspberry Pi OS Lite` (🚨without desktop, only `Lite` version!). You'll find it under category `Raspberry PI OS (other)`
2. Log into your RaspberryPi locally or via ssh (by default it's `ssh pi@raspberrypi.local`)


---
## 📡 Run the studio instance

### with docker run
> ⚠️ `docker ... --rm` option is not suitable for production use because it won't survive a reboot. However, it's okay for quick testing. You need to use --restart=always instead to ensure that it persists.
```bash
# (Optional) Install docker if needed
curl -sSL get.docker.com | sh && sudo usermod -aG docker $(whoami) && logout # then login again

# Prepare application data file tree
cd ~ && mkdir -p obscreen/data/db obscreen/data/uploads && cd obscreen

# Prepare player autostart file
mkdir -p var/run && touch var/run/play && chmod +x var/run/play 

# Run the Docker container
docker run --rm --name obscreen --pull=always \
  -e DEBUG=false \
  -e PORT=5000 \
  -e PLAYER_AUTOSTART_FILE=/app/var/run/play \
  -e SECRET_KEY=ANY_SECRET_KEY_HERE \
  -p 5000:5000 \
  -v ./data/db:/app/data/db \
  -v ./data/uploads:/app/data/uploads \
  -v ./var/run/play:/app/var/run/play \
  jierka/obscreen:latest
```
---
### or with docker compose
```bash
# Prepare application data file tree
cd ~ && mkdir -p obscreen/data/db obscreen/data/uploads obscreen/system && cd obscreen

# Prepare player autostart file
mkdir -p var/run && touch var/run/play && chmod +x var/run/play 

# Download docker-compose.yml
curl https://raw.githubusercontent.com/jr-k/obscreen/master/docker-compose.yml > docker-compose.yml

# Run
docker compose up --detach --pull=always
```
---
### or system wide
#### Install
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y git python3-pip python3-venv libsqlite3-dev

# Get files
cd ~ && git clone https://github.com/jr-k/obscreen.git && cd obscreen

# Install application dependencies
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt

# Customize server default values
cp .env.dist .env
```

#### Configure
- Server configuration is editable in `.env` file.
- Application configuration will be available at `http://raspberrypi.local:5000/settings` page after run.

#### Start server
> ⚠️ Not suitable for production use because it won't survive a reboot. However, it's okay for quick testing. You need to use `systemd` (detailed in next section) to ensure that it persists.
```bash
python ./obscreen.py
```

#### Start server forever with systemctl
```bash
cat "$(pwd)/system/obscreen-studio.service" | sed "s#/home/pi#$HOME#g" | sed "s#=pi#=$USER#g" | sudo tee /etc/systemd/system/obscreen-studio.service
sudo systemctl daemon-reload
sudo systemctl enable obscreen-studio.service
sudo systemctl start obscreen-studio.service
```

#### Troubleshoot
```bash
# Watch logs with following command
sudo journalctl -u obscreen-studio -f 
```
---
## 🏁 Finally
- Run `sudo systemctl restart obscreen-player` or `sudo reboot`

---
## 👌 Usage
- Page which plays slideshow is reachable at `http://raspberrypi.local:5000`
- Slideshow manager is reachable at `http://raspberrypi.local:5000/manage`

---
## 📺 Run the player instance

### Autorun for a RaspberryPi
- Install player autorun by executing following script (will install chromium, x11 and obscreen-player systemd service)
```bash
curl -fsSL https://raw.githubusercontent.com/jr-k/obscreen/master/system/install-autorun-rpi.sh | sudo bash -s -- $USER $HOME
mkdir -p ~/obscreen/var/run
nano ~/obscreen/var/run/play
```
- Copy following script in `~/obscreen/var/run/play` file to enable chromium autorun (replace `http://localhost:5000` by your own `obscreen-studio` instance url)
```
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
```
- Restart
```bash
sudo systemctl restart obscreen-player.service
```

### Manually on any device capable of running chromium
When you run the browser yourself, don't forget to use these flags for chromium browser:
```bash
# chromium or chromium-browser or even chrome
# replace http://localhost:5000 with your obscreen-studio instance url
chromium --disable-features=Translate --ignore-certificate-errors --disable-web-security --disable-restore-session-state --autoplay-policy=no-user-gesture-required --start-maximized --allow-running-insecure-content --remember-cert-error-decisions --noerrdialogs --kiosk --incognito --window-position=0,0 --window-size=1920,1080 --display=:0 http://localhost:5000
```
---

## ✨ You are done now :)
- If everything is set up correctly, the RaspberryPi shall start chromium in fullscreen directly after boot screen and after some seconds of showing the date & time (`views/player/default.jinja.html`) your slideshow shall start and loop endlessly.
- Make sure that `PLAYER_AUTOSTART_FILE` exists and is writeable !

## 📎 Additional

### Hardware checks
- Basic Setup
For basic RaspberryPi setup you can use most of the available guides, for example this one:
https://gist.github.com/blackjid/dfde6bedef148253f987

- HDMI Mode
You may need to set the HDMI Mode on the raspi to ensure the hdmi resolution matches your screen exactly. Here is the official documentation:
https://www.raspberrypi.org/documentation/configuration/config-txt/video.md

However, I used this one: `(2,82) = 1920x1080	60Hz	1080p`

### How to upgrade `obscreen-studio`
>#### with docker run
- Just add `--pull=always` to your `docker run ...` command, you'll get latest version automatically.
>#### or with docker compose
- Just add `--pull=always` to your `docker compose up ...` command, , you'll get latest version automatically.
>#### or system wide
- Execute following script
```bash
cd ~/obscreen
git pull
source ./venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart obscreen-studio.service
```

