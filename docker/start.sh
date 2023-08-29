#!/usr/bin/env bash
duectl-daemon start --log-level=DEBUG

cd /home/application
export PATH=/home/application/.local/bin:$PATH
exec su "application" -c "jupyter-lab"
