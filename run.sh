#!/usr/bin/env bash

export MTAURL=http://datamine.mta.info/mta_esi.php?key=
export MTAKEY=9a707b925e75f2830938dba89a0c62f2
export MTAFEEDID=2

pipenv run python3 mta.py
