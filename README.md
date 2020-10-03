<p align="center">
    <img src="https://raw.githubusercontent.com/Stefankar1000/nagatoro/master/nagatoro.png" width="128">
    <br>
    <b>Nagatoro</b>
    <br>
    <i>A modular bot for various tasks</i>
    <br>
    <br>
    <a href="https://discordapp.com/oauth2/authorize?client_id=672485626179747864&scope=bot&permissions=8262"><sub>Invite Nagatoro to your server<sub></a>
</p>

<br>
<br>

## Global profiles and rankings

You earn experience through typing, then you level up and gain coin rewards. You can trade coins, and in the future™️, you will be able to buy profile or bot perks with them.

![Profile](https://cdn.discordapp.com/attachments/483273472555089930/714646948283547729/unknown.png)

## Moderation

As a moderator, you are able to give users warn and mute punishments.

![Muting](https://cdn.discordapp.com/attachments/483273472555089930/714647821189513226/unknown.png) | ![Warning](https://cdn.discordapp.com/attachments/483273472555089930/714648476495118416/unknown.png)
:-:|:-:

## AniList integration

Thanks to AniList's API, you can see info about you favorite anime, manga, studio and much more on the fly. More features are coming soon™️.

![Anime](https://cdn.discordapp.com/attachments/483273472555089930/714651179405279292/unknown.png) | ![Studio](https://cdn.discordapp.com/attachments/483273472555089930/714651416211226704/unknown.png)
:-:|:-:

# Running Nagatoro
- Make sure you have python version 3.8 or higher installed. You can check by running `python --version` or `python3 --version`.
- In the `data` directory, rename `config.example.json` to `config.json`.
- Create a Discord application and input its token into the config.
- Get a Tenor API key and add it to the config.
- Put credentials to a MySQL database in the config.
- (optional) Set `"testing": true` if you have multiple bot instances (production and testing) running at the same time. `"testing": true` disables counting experience, checking custom prefixes and setting the status. Ideally, you should have a separate database for your testing environment, but I used to have a single db for some time. This option will be deprecated in the future.
- (optional) Create a virtual environment: `python3.8 -m venv`, which you will need to activate every time before running the bot or installing dependencies: `source venv/bin/activate`.
- Install all dependencies: `python3.8 -m pip install -r requirements.txt --upgrade --user`
- Run the bot: `python3.8 nagatoro.py`
