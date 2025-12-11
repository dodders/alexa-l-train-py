#!/usr/bin/env bash

# MTA API no longer requires authentication as of 2024
# The API is free and open to use
export MTAURL=https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l

# Use pipenv from user's Python bin if available, fallback to system pipenv
PIPENV_CMD=${HOME}/Library/Python/3.9/bin/pipenv
if ! command -v pipenv &> /dev/null && [ -f "$PIPENV_CMD" ]; then
    $PIPENV_CMD run python3 mta.py
else
    pipenv run python3 mta.py
fi
