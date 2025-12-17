#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "Must be run as root with sudo"
    exit 1
fi

systemctl enable video_looper.service
systemctl start video_looper.service

