<p align="center">
    <img src="https://raw.githubusercontent.com/Stefankar1000/nagatoro/master/nagatoro.png" width="128" alt="Nagatoro's avatar">
    <br>
    <b>Nagatoro</b>
    <br>
    <a href="https://discordapp.com/oauth2/authorize?client_id=672485626179747864&scope=bot&permissions=8262"><sub>Invite Nagatoro to your server</sub></a>
</p>

<br>
<br>

# Features
### Global profiles and rankings

Earn experience through typing and level up and gain coin rewards. 

![Profile](https://cdn.discordapp.com/attachments/483273472555089930/714646948283547729/unknown.png)

### Moderation

As a moderator, you can mute and warn members on your server.

![Muting](https://cdn.discordapp.com/attachments/483273472555089930/714647821189513226/unknown.png) | ![Warning](https://cdn.discordapp.com/attachments/483273472555089930/714648476495118416/unknown.png)
:-:|:-:

### AniList integration

Thanks to AniList's API, you can see info about you favorite anime, manga, studio and much more on the fly. More features are coming soon™️.

![Anime](https://cdn.discordapp.com/attachments/483273472555089930/714651179405279292/unknown.png) | ![Studio](https://cdn.discordapp.com/attachments/483273472555089930/714651416211226704/unknown.png)
:-:|:-:

# Running Nagatoro
### With Docker
Make sure you have `docker` and `docker-compose` installed.
There are two ways to run Nagatoro through docker:
##### 1: Build the image:
- Clone the repository
- Rename `.env.example` to `.env` and populate it with approperiate configuration variables
- Run `docker-compose up -d` - this should build the image and run the app
- To check logs, use `docker-compose logs`

##### 2: Use the latest public image
- Make a folder called `nagatoro`
- Inside the folder create a file named `docker-compose.yml` with this content:
```
version: "3"

services:
  nagatoro:
    image: ghcr.io/stefankar1000/nagatoro/nagatoro:latest
    restart: unless-stopped
    environment:
      - TOKEN=bot_token
      - PREFIX=prefix
      - ...
```
- Add other variables in the `environment` section, same as in .env.example
- Start with `docker-compose up -d` and check logs with `docker-compose logs`
- To update the image to its latest version, use `docker-compose pull` and restart with `docker-compose up -d`

### Manual
- Make sure you have python version 3.8 or higher installed. You can check by running `python3 --version`
- Rename `.env.example` to `.env` and fill in all required configuration values
- Create a Discord application and input its token into the config
- (optional) Get a Tenor API key and add it to the config
- Put credentials to a MySQL database in the config
- Install all dependencies: `python3.8 -m pip install -r requirements.txt --upgrade --user`
- Run the bot: `python3.8 nagatoro.py`
