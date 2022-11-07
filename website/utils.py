import datetime
import os
from threading import Timer

from humanize import filesize as hf


viewable_formats = {
    "avi", "mp4", "mkv", "wmv",
    "m4v", "webm", "mov", "mpg",

    "tif", "tiff", "bmp", "jpg",
    "jpeg", "gif", "png",

    "wav", "mp3", "wma", "ogg",
    "pcm", "aiff", "aac", "flac",

    "pdf",

    "txt"
}


emojis = {
    "avi": "🎞️", "mp4": "🎞️",
    "wmv": "🎞️", "mkv": "🎞️",
    "webm": "🎞️", "mov": "🎞️",
    "mpg": "🎞️","m4v": "🎞️",

    "tif": "🖼️", "tiff": "🖼️",
    "bmp": "🖼️", "jpg": "🖼️",
    "jpeg": "🖼️", "gif": "🖼️",
    "png": "🖼️", "raw": "🖼️",

    "srt": "ℹ️", "sbv": "ℹ️",

    "wav": "🎵", "mp3": "🎵",
    "wma": "🎵", "ogg": "🎵",
    "pcm": "🎵", "aiff": "🎵",
    "aac": "🎵", "flac": "🎵",

    "pdf": "📕",

    "txt": "📝"
}


class Session:
    def __init__(self, expire, token):
        self.expire = expire
        self.token = token


def autodelete_sessions(sessions):
    Timer(1800, autodelete_sessions, args=(sessions,)).start()

    now = datetime.datetime.now()

    for i, session in enumerate(sessions):
        if session.expire <= now:
            del sessions[i]


def session_is_valid(token, sessions):
    if not token: return False

    for session in sessions:
        if session.token == token: return True

    return False


def get_dir_content(d):
    dir_content = os.listdir(d)
    folders = [item + '/' for item in dir_content if not os.path.isfile(d + "/" + item)]
    files = [(item, hf.naturalsize(os.path.getsize(d + "/" + item))) for item in dir_content if os.path.isfile(d + "/" + item)]
    return files, folders


def emoji_selector(filename):
    _, extension = os.path.splitext(filename)

    # Removing leading dot
    extension = extension[1:]

    return emojis.get(extension.lower(), "📄")


def search_filename(d, name):
    dir_content = os.listdir(d)

    folders = [item + '/' for item in dir_content if not os.path.isfile(os.path.join(d, item))]

    files = []
    for item in dir_content:
        if os.path.isfile(d + item) and name in item.lower().replace("_", " "):
            item_size = hf.naturalsize(os.path.getsize(d + item))
            files.append((d + item, item, item_size))

    return files + sum([search_filename(d + folder, name) for folder in folders], start=[])
