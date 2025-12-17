import os
import subprocess
import time


class USBDriveReader:
    def __init__(self, config):
        self._mount_path = config.get('usb_drive', 'mount_path')
        self._extensions = config.get('video_looper', 'video_extensions').split(',')
        self._extensions = [x.strip().lower() for x in self._extensions]

    def is_mounted(self):
        return os.path.ismount(self._mount_path)

    def mount(self):
        if self.is_mounted():
            return True
        devices = self._find_usb_devices()
        if not devices:
            return False
        for device in devices:
            if self._try_mount(device):
                return True
        return False

    def unmount(self):
        if self.is_mounted():
            subprocess.call(['umount', self._mount_path])

    def get_paths(self):
        if not self.is_mounted():
            return []
        return [self._mount_path]

    def _find_usb_devices(self):
        devices = []
        try:
            result = subprocess.run(
                ['lsblk', '-rno', 'NAME,TRAN'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'usb':
                    base_device = parts[0]
                    result2 = subprocess.run(
                        ['lsblk', '-rno', 'NAME', f'/dev/{base_device}'],
                        capture_output=True,
                        text=True
                    )
                    for subline in result2.stdout.strip().split('\n'):
                        name = subline.strip()
                        if name != base_device:
                            devices.append(f'/dev/{name}')
        except Exception:
            pass
        return devices

    def _try_mount(self, device):
        if not os.path.exists(self._mount_path):
            os.makedirs(self._mount_path)
        result = subprocess.call(
            ['mount', '-o', 'ro', device, self._mount_path],
            stderr=subprocess.DEVNULL
        )
        return result == 0

