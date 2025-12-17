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
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
User=pi
ExecStartPre=/bin/sleep 5
ExecStart=/usr/local/bin/video_looper
Restart=always
RestartSec=3
Environment=DISPLAY=:0
Environment=XDG_RUNTIME_DIR=/run/user/1000

[Install]
WantedBy=graphical.target
EOF

systemctl daemon-reload
systemctl enable video_looper.service
systemctl start video_looper.service

echo "Installation complete"
