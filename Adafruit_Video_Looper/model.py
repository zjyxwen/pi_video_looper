import os
import re


class Movie:
    def __init__(self, filename, title=None, repeats=1):
        self.filename = filename
        self.title = title if title else os.path.basename(filename)
        self.repeats = repeats
        self.playcount = 0


class Playlist:
    def __init__(self, movies):
        self._movies = movies
        self._index = 0

    def get_next(self):
        if len(self._movies) == 0:
            return None
        movie = self._movies[self._index]
        movie.playcount += 1
        if movie.playcount >= movie.repeats:
            movie.playcount = 0
            self._index = (self._index + 1) % len(self._movies)
        return movie

    def length(self):
        return len(self._movies)


def build_playlist(paths, extensions):
    movies = []
    for path in paths:
        if os.path.isdir(path):
            for filename in sorted(os.listdir(path)):
                filepath = os.path.join(path, filename)
                if is_valid_file(filepath, extensions):
                    movies.append(create_movie(filepath))
        elif os.path.isfile(path):
            if is_valid_file(path, extensions):
                movies.append(create_movie(path))
    return Playlist(movies)


def is_valid_file(path, extensions):
    ext = os.path.splitext(path)[1].lower()
    return ext in extensions and os.path.isfile(path)


def create_movie(filepath):
    filename = os.path.basename(filepath)
    name, _ = os.path.splitext(filename)
    repeats = 1
    match = re.search(r'_repeat_(\d+)x', name, re.IGNORECASE)
    if match:
        repeats = int(match.group(1))
    return Movie(filepath, name, repeats)

