import subprocess
import signal
import os


class VideoPlayer:
    def __init__(self, config):
        self._process = None

    def supported_extensions(self):
        return ['.mp4', '.m4v', '.mkv', '.avi', '.mov', '.wmv', '.webm', '.flv', '.mpg', '.mpeg', '.3gp']

    def play(self, movie, loop=None):
        self.stop()
        args = [
            'mpv',
            '--fullscreen',
            '--no-terminal',
            '--no-osc',
            '--no-input-default-bindings',
        ]
        if loop == -1:
            args.append('--loop-file=inf')
        args.append(movie.filename)
        env = os.environ.copy()
        env['DISPLAY'] = ':0'
        self._process = subprocess.Popen(
            args,
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

