# <img src="https://github.com/jr-k/obscreen/blob/master/docs/obscreen.png" width="22"> Obscreen

🧑‍🎄 Open to feature request and pull request

## About
Use a RaspberryPi to show a full-screen slideshow (Kiosk-mode)

[![Docker Pulls](https://badgen.net/docker/pulls/jierka/obscreen?icon=docker&label=docker%20pulls)](https://hub.docker.com/r/jierka/obscreen/)

### Features:
- Dead simple chromium webview
- Clear GUI
- Fleet view to manage many devices easily
- Very few dependencies
- JSON database files
- Plugin system
- No stupid pricing plan
- No cloud
- No telemetry

![Obscreen Screenshot](https://github.com/jr-k/obscreen/blob/master/docs/screenshot.png  "Obscreen Screenshot")

## 🐳 Run with docker
### With docker (for test)
```bash
# Prepare application data file tree
mkdir -p obscreen/data/db obscreen/data/uploads && cd obscreen

# Run the Docker container
# 🚨 If you ARE NOT on a RaspberryPi ignore the line (-v /home/pi/....)
# 🚨 Else make sure that `AUTOCONFIGURE_LX_FILE` exists and is writeable !
docker run --rm --name obscreen --pull=always \
  -e DEBUG=false \
  -e PORT=5000 \
  -e AUTOCONFIGURE_LX_FILE=/app/var/run/lxfile \
  -e SECRET_KEY=ANY_SECRET_KEY_HERE \
  -p 5000:5000 \
  -v ./data/db:/app/data/db \
  -v ./data/uploads:/app/data/uploads \
  -v /home/pi/.config/lxsession/LXDE-pi/autostart:/app/var/run/lxfile \
  jierka/obscreen:latest
```

### With docker-compose
```bash
# Prepare application data file tree
mkdir -p obscreen/data/db obscreen/data/uploads && cd obscreen

# Download docker-compose.yml
curl https://raw.githubusercontent.com/jr-k/obscreen/master/docker-compose.yml > docker-compose.yml

# If you ARE NOT on a RaspberryPi execute the line below
uname | grep -q 'Darwin' && sed -i '' '/\/home\/pi/s/^/#/' docker-compose.yml || sed -i '/\/home\/pi/s/^/#/' docker-compose.yml

# Run
docker compose up
```

## 📠 Run system wide
### Install
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y git chromium-browser unclutter

# Get files
git clone https://github.com/jr-k/obscreen.git && cd obscreen

# Install application dependencies
pip3 install -r requirements.txt

# Add some sample data
cp data/db/slideshow.json.dist data/db/slideshow.json

# Customize server default values
cp .env.dist .env
```

### Configure
- Server configuration is editable in `.env` file.
- Application configuration is available in `http://localhost:5000/settings` page.

### Start server (for test)
```bash
./obscreen.py
```

### Start server forever with systemctl
```bash
sudo ln -s "$(pwd)/system/obscreen.service" /etc/systemd/system/obscreen.service
sudo systemctl daemon-reload
sudo systemctl enable obscreen.service
sudo systemctl start obscreen.service
```

To troubleshoot you can check logs
```bash
sudo journalctl -u obscreen -f 
```

## 👌 Usage
- Page which plays slideshow is reachable at `http://localhost:5000`
- Slideshow manager is reachable at `http://localhost:5000/manage`
    
## ✨ You are done now :)
- If everything is set up correctly, the RaspberryPi shall start chromium in fullscreen directly after boot screen and after some seconds of showing the date & time (`views/player/default.jinja.html`) your slideshow shall start and loop endlessly.
- Make sure that `AUTOCONFIGURE_LX_FILE` exists and is writeable !

## 📎 Additional

### Hardware checks
- Basic Setup
For basic RaspberryPi setup you can use most of the available guides, for example this one:
https://gist.github.com/blackjid/dfde6bedef148253f987

- HDMI Mode
You may need to set the HDMI Mode on the raspi to ensure the hdmi resolution matches your screen exactly. Here is the official documentation:
https://www.raspberrypi.org/documentation/configuration/config-txt/video.md

However, I used this one: `(2,82) = 1920x1080	60Hz	1080p`
