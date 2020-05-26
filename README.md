<p align="center">
    <img src="nagatoro.png" width="128">
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

# Running your own fork
You need to make a config file, that will be located in `data/config.json`.
Look into `nagatoro/objects/config.py` to see what is needed to be put in there.
You can use different types of databases, but they need to support the BIGINT
type. Modify the config.json/config.py/database.py file according to pony.orm documentation
if you wish to use different database.
Install the requirements provided in requirements.txt via pip, and make sure you
are running at least python version 3.8.
