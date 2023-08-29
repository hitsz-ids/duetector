#!/usr/bin/env bash
duectl-daemon start --loglevel=DEBUG

cd /home/application
export PATH=/home/application/.local/bin:$PATH
exec su "application" -c "jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser"
