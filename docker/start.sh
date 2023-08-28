#!/usr/bin/env bash
cd /root
exec duectl start 2>&1 &

cd /home/application
exec su "application"
