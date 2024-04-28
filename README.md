# <img src="https://github.com/jr-k/obscreen/blob/master/docs/obscreen.png" width="22"> Obscreen

🧑‍🎄 Open to feature request and pull request

## About
Use a RaspberryPi to show a full-screen slideshow (Kiosk-mode)

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

## Installation (docker)
```bash
git clone https://github.com/jr-k/obscreen.git
cd obscreen
docker compose up
```

## Installation (manual)
```bash
sudo apt-get update
sudo apt-get install -y git chromium-browser unclutter

git clone https://github.com/jr-k/obscreen.git 
cd obscreen && pip3 install -r requirements.txt && cp data/db/slideshow.json.dist data/db/slideshow.json && cp config.json.dist config.json
```

## Configure
- Server configuration is available in `config.json` file.
- Application configuration is available in `http://localhost:5000/settings` page.

## Run

### Cli mode
```bash
./obscreen.py
```

### Forever with systemctl
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

## Usage
- Hostname will be http://localhost:5000 or http://localhost with nginx or http://[SERVER_IP]:[PORT]
- Page which plays slideshow is reachable at `http://localhost:5000`
- Slideshow manager is reachable at `http://localhost:5000/manage`
    
## You are done now :)
If everything is set up correctly, the RaspberryPi shall start chromium in fullscreen directly after boot screen and after some seconds of showing the date & time (`views/player/default.jinja.html`) your slideshow shall start and loop endlessly.


## Additional

### A. Hardware checks
- Basic Setup
For basic RaspberryPi setup you can use most of the available guides, for example this one:
https://gist.github.com/blackjid/dfde6bedef148253f987

- HDMI Mode
You may need to set the HDMI Mode on the raspi to ensure the hdmi resolution matches your screen exactly. Here is the official documentation:
https://www.raspberrypi.org/documentation/configuration/config-txt/video.md

However, I used this one: `(2,82) = 1920x1080	60Hz	1080p`

### B. Nginx server to serve pages (useful for gzip compression for instance)
1. Install
```bash
sudo apt install -y nginx
sudo rm /etc/nginx/sites-enabled/default 2>/dev/null
sudo ln -s "$(pwd)/system/nginx-obscreen" /etc/nginx/sites-enabled
sudo systemctl reload nginx
```
2. Set `reverse_proxy_mode` to `true` in server `config.js` file
