# Nagatoro
## A simple, general purpose Discord bot
This bot is still in early development stages, so expect things to change, not work on some occasions or break over night when it decides, that the new feature I just added is bad.

# Features
- Global levelling and balance
- Global level/balance ranking
- Action commands (pat, hug, etc.)
- Custom prefix
- A few utility commands

# Running your own fork
You need to make a config file, that will be located in `data/config.json`.
Look into `nagatoro/objects/config.py` to see what is needed to be put in there.
You can use different types of databases, but they need to support the BIGINT
type. Modify the config.json/config.py/database.py file according to pony.orm documentation
if you wish to use different database.
Install the requirements provided in requirements.txt via pip, and make sure you
are running at least python version 3.8.
