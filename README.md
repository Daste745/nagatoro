<p align="center">
    <img src="https://raw.githubusercontent.com/daste745/nagatoro/master/nagatoro.png" width="128" alt="Nagatoro's avatar">
    <br>
    <b>Nagatoro</b>
    <br>
    <a href="https://discordapp.com/oauth2/authorize?client_id=672485626179747864&scope=bot&permissions=8262"><sub>Invite Nagatoro to your server</sub></a>
</p>

[![License](https://img.shields.io/github/license/daste745/nagatoro?style=flat-square)](./LICENSE)
[![Issues](https://img.shields.io/github/issues/daste745/nagatoro?style=flat-square)](https://github.com/daste745/nagatoro/issues)
[![Discord](https://img.shields.io/discord/675787405889896478?logo=discord&style=flat-square)](https://discord.gg/qDzU7gd)

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
### Docker
Make sure you have `docker` and `docker-compose` installed.

There are two ways to run Nagatoro through docker:
##### Build the image:
- Clone the repository
- Rename `.env.example` to `.env` and populate it with approperiate configuration variables
- Run `docker-compose up -d` - this should build the image and start the application stack

#### Or Use the latest public image:
- Make a folder called `nagatoro`
- Copy the [`docker-compose.yml`](./docker-compose.yml) file to this directory
- Under `services>nagatoro` replace the line containing `build .` with `image: ghcr.io/daste745/nagatoro/nagatoro:latest` to use the latest public image, without needing to build it every time
- Copy [`env.example`](./.env.example), rename it to `.env` and change the configuration variables appropriately
- Copy [`redis.conf`](./redis.conf) to your directory
- Run `docker-compose up -d` - this should pull the latest public image and start the application stack
- Use `docker-compose pull` to update and restart the stack with `docker-compose up -d`

To check logs, use `docker-compose logs` or `docker-compose logs nagatoro` if you only want to see bot logs

### Manual
- Make sure you have python version 3.8 or higher installed. You can check by running `python3 --version`
- Rename `.env.example` to `.env` and fill in all required configuration values
- Create a Discord application and input its token into the config
- (optional) Get a Tenor API key and add it to the config
- Put credentials to a MySQL database in the config
- Install all dependencies: `python3.8 -m pip install -r requirements.txt --upgrade --user`
- Run the bot: `python3.8 nagatoro.py`
