# <img src="https://github.com/jr-k/obscreen/blob/master/docs/img/obscreen.png" width="22"> Obscreen - Headless run on any server

> #### 👈 [back to readme](/README.md)

#### 🔵 You just want a slideshow manager and you'll deal with screen and browser yourself ? You're in the right place.


---
## 📡 Run the manager

### with docker run (for test)
```bash
# (Optional) Install docker if needed
curl -sSL get.docker.com | sh && sudo usermod -aG docker $(whoami) && logout # then login again

# Prepare application data file tree
cd ~ && mkdir -p obscreen/data/db obscreen/data/uploads && cd obscreen

# Run the Docker container
docker run --rm --name obscreen --pull=always \
  -e DEBUG=false \
  -e PORT=5000 \
  -e PLAYER_AUTOSTART_FILE=/app/var/run/play \
  -e SECRET_KEY=ANY_SECRET_KEY_HERE \
  -p 5000:5000 \
  -v ./data/db:/app/data/db \
  -v ./data/uploads:/app/data/uploads \
  -v /dev/null:/app/var/run/play \
  jierka/obscreen:latest
```
---
### or with docker compose
```bash
# Prepare application data file tree
cd ~ && mkdir -p obscreen/data/db obscreen/data/uploads && cd obscreen

# Download docker-compose.yml
curl https://raw.githubusercontent.com/jr-k/obscreen/master/docker-compose.headless.yml > docker-compose.yml

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

# 🚨For MacOS users, requirements installation may cause an error but it's ok if only for pysqlite3 package
#   you'll need to install brew and execute command `brew install sqlite3`
pip install -r requirements.txt

# Customize server default values
cp .env.dist .env
```

#### Configure
- Server configuration is editable in `.env` file.
- Application configuration will be available at `http://localhost:5000/settings` page after run.

#### Start server (for test)
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

## 👌 Usage
- Page which plays slideshow is reachable at `http://localhost:5000`
- Slideshow manager is reachable at `http://localhost:5000/manage`


---
## 📺 Run the player
When you run the browser yourself don't forget to use these flags for chromium browser:
```bash
# chromium or chromium-browser or even chrome
# replace http://localhost:5000 with your playlist url
chromium --disable-features=Translate --ignore-certificate-errors --disable-web-security --disable-restore-session-state --autoplay-policy=no-user-gesture-required --start-maximized --allow-running-insecure-content --remember-cert-error-decisions --noerrdialogs --kiosk --incognito --window-position=0,0 --window-size=1920,1080 --display=:0 http://localhost:5000
```
---

## 📎 Additional


### How to upgrade
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
