# <img src="https://github.com/jr-k/obscreen/blob/master/docs/img/obscreen.png" width="22"> Obscreen v2


🧑‍🎄 Open to feature request and pull request

**⭐️ You liked it ? Give this repository a star, it's free :)**

## About
Use a RaspberryPi (Lite OS) to show a fullscreen slideshow (Kiosk-mode)

[![Docker Pulls](https://badgen.net/docker/pulls/jierka/obscreen?icon=docker&label=docker%20pulls)](https://hub.docker.com/r/jierka/obscreen/)

### Features:
- Dead simple chromium webview
- Clear GUI
- Very few dependencies
- SQLite database
- Plugin system
- Feature flags to enable complex use cases (Fleet/User/Playlist management)
- No stupid pricing plan
- No cloud
- No telemetry

![Obscreen Screenshot](https://github.com/jr-k/obscreen/blob/master/docs/screenshot-playlist-edit.png  "Obscreen Screenshot")

# Cookbooks

### 🔴 [I want to power a RaspberryPi and automatically see my slideshow on a screen connected to it and manage the slideshow](docs/setup-run-on-rpi.md)
### 🔵 [I just want a slideshow manager and I'll deal with screen and browser myself](docs/setup-run-headless.md)
 
# Discussion

### Join our Discord
[<img src="https://github.com/jr-k/obscreen/blob/master/docs/img/discord.png" width="64">](https://discord.obscreen.io)

### Open an Issue or a Pull Request on Github
[<img src="https://github.com/jr-k/obscreen/blob/master/docs/img/github.png" width="64">](https://github.com/jr-k/obscreen/issues/new/choose)

# Troubleshoot

### Videos aren't playing why ?
This is "normal" behavior. Videos do not play automatically in Chrome because it requires user interaction with the page (a simple click inside the webpage is enough). If you open the console, you'll see the error: [Uncaught (in promise) DOMException: play() failed because the user didn't interact with the document first...](https://goo.gl/xX8pDD)

To resolve this, you need to use the Chrome flag --autoplay-policy=no-user-gesture-required. When connecting a Raspberry Pi with Obscreen Player autorun, this issue doesn't occur because the flag is handled automatically for you.You need to enable this flag yourself otherwise.
