#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "Must be run as root with sudo"
    exit 1
fi

apt-get update
apt-get install -y vlc python3-pip

mkdir -p /mnt/usbdrive

if [ -f /boot/firmware/config.txt ]; then
    cp video_looper.ini /boot/firmware/video_looper.ini
else
    cp video_looper.ini /boot/video_looper.ini
fi

pip3 install . --break-system-packages

cat > /etc/systemd/system/video_looper.service << EOF
[Unit]
Description=Pi Video Looper
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/local/bin/video_looper
Restart=always
RestartSec=3
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable video_looper.service
systemctl start video_looper.service

echo "Installation complete"

