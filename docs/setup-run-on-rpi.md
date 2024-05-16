# <img src="https://github.com/jr-k/obscreen/blob/master/docs/img/obscreen.png" width="22"> Obscreen - Autorun on RaspberryPi

> #### 👈 [back to readme](/README.md)

#### 🔴 You want to power RaspberryPi and automatically see your slideshow on a screen connected to it and manage your slideshow ? You're in the right place.

## 🎛️ Hardware installation

1. Download RaspberryPi Imager and setup an sdcard with `Raspberry Pi OS Lite` (🚨without desktop, only `Lite` version!). You'll find it under category `Raspberry PI OS (other)`
2. Log into your pi user locally or via ssh (`ssh pi@raspberrypi.local`)
3. Install player autorun by executing `curl -fsSL https://raw.githubusercontent.com/jr-k/obscreen/master/system/install-autorun-rpi.sh | sudo bash`

---
## 🐳 Run with docker
### Install docker if needed
```bash
curl -sSL get.docker.com | sh
sudo usermod -aG docker $(whoami)
logout
#then login again
```


### With docker (for test)
```bash
# Prepare application data file tree and prepare player autostart file
cd /home/pi && mkdir -p obscreen/data/db obscreen/data/uploads obscreen/system && touch system/start-chromium.sh && cd obscreen

# Run the Docker container
ocker run --rm --name obscreen --pull=always \
  -e DEBUG=false \
  -e PORT=5000 \
  -e PLAYER_AUTOSTART_FILE=/app/var/run/play \
  -e SECRET_KEY=ANY_SECRET_KEY_HERE \
  -p 5000:5000 \
  -v ./data/db:/app/data/db \
  -v ./data/uploads:/app/data/uploads \
  -v /home/pi/obscreen/system/start-chromium.sh:/app/var/run/play \
  jierka/obscreen:latest
```

### Or with docker-compose
```bash
# Prepare application data file tree
cd /home/pi && mkdir -p obscreen/data/db obscreen/data/uploads obscreen/system && touch system/start-chromium.sh && cd obscreen

# Download docker-compose.yml
curl https://raw.githubusercontent.com/jr-k/obscreen/master/docker-compose.yml > docker-compose.yml

# Run
docker compose up --detach --pull always
```
---
## 📠 Run system wide
### Install
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y git xinit xserver-xorg chromium-browser unclutter python3-venv python3-pip

# Get files
git clone https://github.com/jr-k/obscreen.git && cd obscreen

# Install application dependencies
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt

# Add some sample data
cp data/db/slideshow.json.dist data/db/slideshow.json

# Customize server default values
cp .env.dist .env
```

### Configure
- Server configuration is editable in `.env` file.
- Application configuration will be available at `http://raspberrypi.local:5000/settings` page after run.

### Start server (for test)
```bash
python3 ./obscreen.py
```

### Start server forever with systemctl
```bash
sudo ln -s "$(pwd)/system/obscreen-manager.service" /etc/systemd/system/obscreen-manager.service
sudo systemctl daemon-reload
sudo systemctl enable obscreen-manager.service
sudo systemctl start obscreen-manager.service
```

To troubleshoot you can check logs
```bash
sudo journalctl -u obscreen -f 
```
---
## 👌 Usage
- Page which plays slideshow is reachable at `http://raspberrypi.local:5000`
- Slideshow manager is reachable at `http://raspberrypi.local:5000/manage`
    
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


