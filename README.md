# Obscreen

## About
Use a RaspberryPi to show a full-screen Slideshow (Kiosk-mode)

## Installation TL;DR
```bash
sudo apt-get update && sudo apt-get dist-upgrade
sudo apt-get install -y git chromium-browser unclutter

git clone https://github.com/jr-k/obscreen.git 
cd obscreen && pip3 install -r requirements.txt && cp data/slideshow.json.dist data/slideshow.json
./obscreen.py
```

## Installation - step by step
### Basic Setup
For basic RaspberryPi setup you can use most of the available guides, for example this one:
https://gist.github.com/blackjid/dfde6bedef148253f987

### HDMI Mode
You may need to set the HDMI Mode on the raspi to ensure the hdmi resolution matches your screen exactly. Here is the official documentation:
https://www.raspberrypi.org/documentation/configuration/config-txt/video.md

However, I used this one: `(2,82) = 1920x1080	60Hz	1080p`

### Installation of base software
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
sudo apt-get install -y git chromium-browser unclutter

git clone https://github.com/jr-k/obscreen.git 
cd obscreen && pip3 install -r requirements.txt && cp data/slideshow.json.dist data/slideshow.json
```

### Optional
1. Nginx server to serve pages (useful for gzip compression for instance)
```bash
sudo apt isntall -y nginx
sudo rm /etc/nginx/sites-enabled/default 2>/dev/null
sudo ln -s "$(pwd)/system/nginx-obscreen" /etc/nginx/sites-enabled
sudo systemctl reload nginx
```

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

## Prepare your Slideshow
Everything slideshow-related happens in the ./data/uploads folder.
- Put some images into the /data/uploads folder. Ideally with the same resolution of the screen (eg. 1920x1080px). 
- Edit the slideshow.json
    
## You are done now :)
If everything is set up correctly, the RaspberryPi shall start chromium in fullscreen directly after boot screen and after some seconds of showing the date & time (default.html) your slideshow shall start and loop endlessly.

