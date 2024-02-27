![Obscreen Logo](https://github.com/jr-k/obscreen/blob/master/docs/obscreen.png  "Obscreen Logo")

# Obscreen

## About
Use a RaspberryPi to show a full-screen slideshow (Kiosk-mode)

![Obscreen Screenshot](https://github.com/jr-k/obscreen/blob/master/docs/screenshot.png  "Obscreen Screenshot")

## Installation
```bash
sudo apt-get update
sudo apt-get install -y git chromium-browser unclutter

git clone https://github.com/jr-k/obscreen.git 
cd obscreen && pip3 install -r requirements.txt && cp data/slideshow.json.dist data/slideshow.json && cp config.py.dist config.py
```

## Configure
- Server configuration is available in `config.py` file.

## Run

### Cli mode
```bash
./obscreen.py
```

### Forever with systemctl
```bash
sudo cp system/obscreen.service /etc/systemd/system/obscreen.service
sudo systemctl daemon-reload
sudo systemctl enable obscreen.service
sudo systemctl start obscreen.service
```

## Usage
- Hostname will be http://localhost:5000 or http://localhost with nginx or http://[SERVER_IP]:[PORT]
- Page which play slideshow is reachable at `http://localhost:5000`
- Slideshow manager is reachable at `http://localhost:5000/manage`
    
## You are done now :)
If everything is set up correctly, the RaspberryPi shall start chromium in fullscreen directly after boot screen and after some seconds of showing the date & time (default.html) your slideshow shall start and loop endlessly.


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
sudo apt isntall -y nginx
sudo rm /etc/nginx/sites-enabled/default 2>/dev/null
sudo ln -s "$(pwd)/system/nginx-obscreen" /etc/nginx/sites-enabled
sudo systemctl reload nginx
```
2. Configure `nano config.py`
```js
{
// ...
    "reverse_proxy_mode": True,
// ...
}
```
