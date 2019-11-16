#!/usr/bin/env bash

SITE=~/.local/share/virtualenvs/alexa-l-train-py-2ECeZEfi/lib/python3.7/site-packages
FILES=`ls *.py | grep -v test`

echo installing from $SITE...
mkdir target
cp -r $SITE/* target/
rm -rf target/__pycache__
echo moving $FILES...
cp $FILES target/
cd target/
zip ../lambda-package.zip *
cd ..
rm -rf target
echo lambda-package.zip created.

