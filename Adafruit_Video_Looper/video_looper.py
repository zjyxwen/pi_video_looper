#!/usr/bin/env python3

import configparser
import os
import sys
import time
import signal
import threading

from .model import build_playlist
from .usb_drive import USBDriveReader
from .video_player import VideoPlayer


class VideoLooper:
    def __init__(self, config_path):
        self._running = False
        self._exit_requested = False
        self._stop_event = threading.Event()
        self._config = configparser.ConfigParser()
        self._config.read(config_path)
        self._usb = USBDriveReader(self._config)
        self._player = VideoPlayer(self._config)
        self._playlist = None
        self._wait_time = self._config.getfloat('video_looper', 'wait_time')
        self._extensions = self._config.get('video_looper', 'video_extensions').split(',')
        self._extensions = [x.strip().lower() for x in self._extensions]

    def _start_esc_listener(self):
        try:
            from evdev import InputDevice, ecodes, list_devices
        except Exception:
            return

        def watch(dev_path):
            try:
                dev = InputDevice(dev_path)
                for event in dev.read_loop():
                    if self._stop_event.is_set():
                        return
                    if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_ESC and event.value == 1:
                        self._running = False
                        self._exit_requested = True
                        self._stop_event.set()
                        try:
                            self._player.stop()
                        except Exception:
                            pass
                        return
            except Exception:
                return

        for dev_path in list_devices():
            t = threading.Thread(target=watch, args=(dev_path,), daemon=True)
            t.start()

    def _build_playlist(self):
        paths = self._usb.get_paths()
        if not paths:
            return None
        return build_playlist(paths, self._extensions)

    def _idle_message(self):
        print('Waiting for USB drive...')

    def run(self):
        self._running = True
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        self._start_esc_listener()

        while self._running:
            if not self._usb.is_mounted():
                if not self._usb.mount():
                    self._idle_message()
                    time.sleep(1)
                    continue

            self._playlist = self._build_playlist()
            if self._playlist is None or self._playlist.length() == 0:
                self._idle_message()
                time.sleep(1)
                continue

            single_video = self._playlist.length() == 1
            player_loop = -1 if single_video else None

            movie = self._playlist.get_next()
            if movie is not None:
                self._player.play(movie, loop=player_loop)

            while self._running and self._player.is_playing():
                if not self._usb.is_mounted():
                    self._player.stop()
                    self._playlist = None
                    break
                time.sleep(0.1)

            if not single_video and self._running and self._usb.is_mounted():
                while self._running and self._usb.is_mounted():
                    movie = self._playlist.get_next()
                    if movie is None:
                        break
                    self._player.play(movie, loop=None)
                    while self._running and self._player.is_playing():
                        if not self._usb.is_mounted():
                            self._player.stop()
                            break
                        time.sleep(0.1)
                    if self._wait_time > 0:
                        time.sleep(self._wait_time)

        self._player.stop()
        if self._exit_requested:
            sys.exit(42)

    def _signal_handler(self, signum, frame):
        self._running = False
        self._stop_event.set()


def main():
    config_path = '/boot/firmware/video_looper.ini'
    if not os.path.exists(config_path):
        config_path = '/boot/video_looper.ini'
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    looper = VideoLooper(config_path)
    looper.run()


if __name__ == '__main__':
    main()
