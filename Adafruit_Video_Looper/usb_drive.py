import os
import glob


class USBDriveReader:
    def __init__(self, config):
        self._media_path = '/media'
        self._extensions = config.get('video_looper', 'video_extensions').split(',')
        self._extensions = [x.strip().lower() for x in self._extensions]

    def is_mounted(self):
        paths = self._find_mounted_drives()
        return len(paths) > 0

    def mount(self):
        return self.is_mounted()

    def unmount(self):
        pass

    def get_paths(self):
        return self._find_mounted_drives()

    def _find_mounted_drives(self):
        paths = []
        for user_dir in glob.glob(os.path.join(self._media_path, '*')):
            if os.path.isdir(user_dir):
                for drive_dir in glob.glob(os.path.join(user_dir, '*')):
                    if os.path.isdir(drive_dir) and os.path.ismount(drive_dir):
                        paths.append(drive_dir)
        return paths
