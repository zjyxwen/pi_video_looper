import subprocess
import signal
import os
import shutil


class VideoPlayer:
    def __init__(self, config):
        self._process = None
        self._ram_file = None
        # Create tmpfs directory for RAM-based playback
        self._tmpdir = '/dev/shm/video_looper'
        os.makedirs(self._tmpdir, exist_ok=True)

    def supported_extensions(self):
        return ['.mp4', '.m4v', '.mkv', '.avi', '.mov', '.wmv', '.webm', '.flv', '.mpg', '.mpeg', '.3gp']

    def play(self, movie, loop=None):
        self.stop()

        video_path = movie.filename

        # For looping: copy video to RAM (tmpfs) for zero-latency seeks
        if loop == -1:
            ram_path = os.path.join(self._tmpdir, os.path.basename(movie.filename))
            try:
                shutil.copy2(movie.filename, ram_path)
                video_path = ram_path
                self._ram_file = ram_path
            except (IOError, OSError):
                # Fall back to original file if copy fails
                pass

        args = [
            'mpv',
            '--fs',
            '--no-terminal',
            '--no-input-terminal',
            '--really-quiet',
            '--no-osc',
            '--no-input-default-bindings',
            '--hwdec=auto',
        ]
        if loop == -1:
            args.append('--loop-file=inf')

        args.append(video_path)

        env = os.environ.copy()
        env['DISPLAY'] = ':0'
        self._process = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
        )

    def is_playing(self):
        if self._process is None:
            return False
        return self._process.poll() is None

    def stop(self):
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
        # Clean up RAM copy
        if self._ram_file and os.path.exists(self._ram_file):
            try:
                os.remove(self._ram_file)
            except OSError:
                pass
            self._ram_file = None
