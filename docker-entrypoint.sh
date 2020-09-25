#!/bin/bash
if [ ! -d "/app/data/action_config.json" ]; then
    cp /app/data-example/action_config.json /app/data -v
fi
cd /app
python3 -u nagatoro.py