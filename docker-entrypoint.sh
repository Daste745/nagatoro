#!/bin/bash
if [ ! -d "/app/data/action_config.json" ]; then
    cp /app/data-example/action_config.json /app/data -v
    echo 1
fi
if [ ! -d "/app/data/config.json" ] || [ ! -d "/app/data/config.example.json" ]; then
    cp /app/data-example/config.example.json /app/data -v
    echo 2
fi
cd /app
echo 0
python3 -u nagatoro.py