from enum import StrEnum
from dataclasses import dataclass


class YoutubeLink(StrEnum):
    VIDEO = "VIDEO"
    PLAYLIST = "PLAYLIST"
    CHANNEL = "CHANNEL"
    BAD_LINK = "BAD_LINK"


class AudioExt(StrEnum):
    OPUS = "opus"
    MP3 = "mp3"
    M4A = "m4a"
    WEBM = "webm"


@dataclass
class Snippet:
    title: str
    url: str
    published: str


@dataclass
class Metadata:
    title: str
    artist: str
    date: str
    comment: str


@dataclass
class DownloadCallback:
    audio_path: str
    thumbnail_path: str
    metadata: Metadata
    bitrate_check: bool


class Attempt(StrEnum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SHORTS = "SHORTS"
