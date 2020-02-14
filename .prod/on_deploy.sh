#!/bin/bash
set -e

./manage.py migrate --noinput
./manage.py import_features
