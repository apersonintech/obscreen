<div align="center" width="100%">
    <img src="./docs/img/obscreen.png" width="128" alt="" />
</div>

# Obscreen

Obscreen is a user-friendly self-hosted digital signage tool. Manage a fleet of Raspberry Pi devices to transform your screens into a professional digital signage network.

<a target="_blank" href="https://github.com/jr-k/obscreen"><img src="https://img.shields.io/github/stars/jr-k/obscreen?style=flat" /></a> <a target="_blank" href="https://hub.docker.com/r/jierka/obscreen"><img src="https://img.shields.io/docker/pulls/jierka/obscreen" /></a> <a target="_blank" href="https://hub.docker.com/r/jierka/obscreen"><img src="https://img.shields.io/docker/v/jierka/obscreen/latest?label=docker%20image%20ver." /></a> <a target="_blank" href="https://github.com/jr-k/obscreen"><img src="https://img.shields.io/github/last-commit/jr-k/obscreen" /></a> 

<img src="https://github.com/jr-k/obscreen/blob/master/docs/screenshot-playlist-edit.png" width="700" alt="" />


## 🕹️ Live Demo

Try it!

Demo Server (Location: Roubaix - France): [https://demo.obscreen.io](https://demo.obscreen.io?username=admin&password=admin)

It is a temporary live demo, all data will be deleted after 10 minutes. Sponsored by myself.

## ⭐️ Features
- Dead simple chromium webview inside
- Fancy graphical user interface
- Very few dependencies
- Embeddable SQLite database
- Fleet screen management
- Playlist management
- Authentication management
- Plugin system to extend capabilities
- [Multi Languages](https://github.com/jr-k/obscreen/tree/master/lang)
- No costly monthly pricing plan per screen or whatever, no cloud, no telemetry

## 👨‍🍳 Cookbooks

### 🔴 [I want to power a RaspberryPi and automatically see my slideshow on a screen connected to it and manage the slideshow](docs/setup-run-on-rpi.md)
### 🔵 [I just want a slideshow manager and I'll deal with screen and browser myself](docs/setup-run-headless.md)

## 📸 More Screenshots

Light Mode:

<img src="https://github.com/jr-k/obscreen/blob/master/docs/screenshot-light-mode.png" width="512" alt="" />

Content Explorer:

<img src="https://github.com/jr-k/obscreen/blob/master/docs/screenshot-content-explorer.png" width="512" alt="" />

Settings Page:

<img src="https://github.com/jr-k/obscreen/blob/master/docs/screenshot-settings.png" width="512" alt="" />

Add Content Modal:

<img src="https://github.com/jr-k/obscreen/blob/master/docs/screenshot-add-content.png" width="512" alt="" />

## 🫡 Motivation

- I was searching for a self-hosted monitoring tool similar to "Screenly", but struggled with "Anthias" (formerly Screenly OSE) due to compatibility issues on some webpages. Chromium does a great job at rendering webpages, so I decided to create my own solution based on browsers.
- Enjoy a beautiful graphical interface
- My goal was to keep the code as simple as possible, using reliable technology with minimal dependencies.
- Aim to showcase the power of the Raspberry Pi 5.
- Deploy my first true Docker image to Docker Hub using a continuous deployment pipeline.

If you value this project, please think about awarding it a ⭐. Thanks ! 🙏

## 🛟 Discussion / Need help ?

### Join our Discord
[<img src="https://github.com/jr-k/obscreen/blob/master/docs/img/discord.png" width="64">](https://discord.obscreen.io)

### Open an Issue
[<img src="https://github.com/jr-k/obscreen/blob/master/docs/img/github.png" width="64">](https://github.com/jr-k/obscreen/issues/new/choose)

### Troubleshoot


<details closed>
<summary><h5>Videos aren't playing why ?</h3></summary>

This is "normal" behavior. Videos do not play automatically in Chrome because it requires user interaction with the page (a simple click inside the webpage is enough). If you open the console, you'll see the error: [Uncaught (in promise) DOMException: play() failed because the user didn't interact with the document first...](https://goo.gl/xX8pDD)

To resolve this, you need to use the Chrome flag --autoplay-policy=no-user-gesture-required. When connecting a Raspberry Pi with Obscreen Player autorun, this issue doesn't occur because the flag is handled automatically for you.You need to enable this flag yourself otherwise.

---

</details>

## 👑 Contributions

### Create Pull Requests

We accept all types of pull requests.

### Test Beta Version

Check out the latest beta release here: https://github.com/jr-k/obscreen/releases

### Translations

If you want to translate Obscreen into your language, please visit [Languages Files](https://github.com/jr-k/obscreen/blob/master/lang).

### Spelling & Grammar

Feel free to correct the grammar in the documentation or code.
My mother language is not English and my grammar is not that great.
