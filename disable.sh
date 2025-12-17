#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "Must be run as root with sudo"
    exit 1
fi

systemctl stop video_looper.service
systemctl disable video_looper.service

