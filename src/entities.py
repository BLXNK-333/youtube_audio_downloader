from enum import StrEnum
from dataclasses import dataclass


class YoutubeLink(StrEnum):
    VIDEO = "VIDEO"
    PLAYLIST = "PLAYLIST"
    BAD_LINK = "BAD_LINK"


class AudioExt(StrEnum):
    OGG = "ogg"
    MP3 = "mp3"
    M4A = "m4a"
    WEBM = "webm"
    BEST_ = "best/bestaudio"


@dataclass
class Snippet:
    title: str
    url: str
    published: str
