#!/usr/bin/env bash
mount -t debugfs debugfs /sys/kernel/debug # enable debugfs
duectl-daemon start --loglevel=DEBUG
duectl-server-daemon start --loglevel=DEBUG

cd /home/application
# Config user's local path for pip install some scripts
export PATH=/home/application/.local/bin:$PATH
exec su "application" -c "jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser"
