#!/bin/sh

source /venv/bin/activate

# Pre-run steps like migrations and waiting for the database go here...

exec "$@"
