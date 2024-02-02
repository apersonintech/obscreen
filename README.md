# Reclame

## About
Use a RaspberryPi to show a full-screen Slideshow (Kiosk-mode)

## Installation TL;DR
```bash
sudo apt-get update && sudo apt-get dist-upgrade
sudo apt-get install git chromium-browser -y

git clone https://github.com/jr-k/reclame.git 
cd reclame && pip3 install -r requirements.txt && cp data/slideshow.json.dist data/slideshow.json
./reclame.py
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
sudo apt-get install git chromium-browser -y

git clone https://github.com/jr-k/reclame.git 
cd reclame && pip3 install -r requirements.txt && cp data/slideshow.json.dist data/slideshow.json
./reclame.py
```

## Prepare your Slideshow
Everything slideshow-related happens in the ./data/uploads folder.
- Put some images into the /data/uploads folder. Ideally with the same resultion of the screen (eg. 1920x1080px). 
- Edit the slideshow.json
    
## You are done now :)
If everything is set up correctly, the RaspberryPi shall start chromium in fullscreen directly after bootup and after some seconds of showing the date & time (default.html) your slideshow shall start and loop endlessly.
