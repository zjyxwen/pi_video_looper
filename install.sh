#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "Must be run as root with sudo"
    exit 1
fi

apt-get update
apt-get install -y mpv python3-pip python3-evdev

if [ -f /boot/firmware/config.txt ]; then
    cp video_looper.ini /boot/firmware/video_looper.ini
else
    cp video_looper.ini /boot/video_looper.ini
fi

pip3 install . --break-system-packages

CURRENT_USER=$(logname)
CURRENT_UID=$(id -u "${CURRENT_USER}")

cat > /etc/systemd/system/video_looper.service << EOF
[Unit]
Description=Pi Video Looper
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
User=${CURRENT_USER}
SupplementaryGroups=input
ExecStartPre=/bin/sleep 5
ExecStart=/usr/local/bin/video_looper
Restart=on-failure
RestartSec=3
SuccessExitStatus=42
Environment=DISPLAY=:0
Environment=XDG_RUNTIME_DIR=/run/user/${CURRENT_UID}

[Install]
WantedBy=graphical.target
EOF

systemctl daemon-reload
systemctl enable video_looper.service
systemctl start video_looper.service

echo "Installation complete"
