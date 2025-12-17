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
        env = os.environ.copy()
        env['DISPLAY'] = ':0'
        if loop == -1:
            script = 'while true; do ffplay -fs -autoexit -loglevel quiet "{}"; done'.format(movie.filename)
            self._process = subprocess.Popen(
                ['bash', '-c', script],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                preexec_fn=os.setsid
            )
        else:
            args = [
                'ffplay',
                '-fs',
                '-autoexit',
                '-loglevel', 'quiet',
                movie.filename
            ]
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
            try:
                os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            except (ProcessLookupError, OSError):
                pass
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    pass
            self._process = None
