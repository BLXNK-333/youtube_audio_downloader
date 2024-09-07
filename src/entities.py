from enum import StrEnum


class YoutubeLink(StrEnum):
    VIDEO = "VIDEO"
    PLAYLIST = "PLAYLIST"
    BAD_LINK = "BAD_LINK"


class AudioExt(StrEnum):
    OGG = "ogg"
    MP3 = "mp3"
    M4A = "m4a"
    WEBM = "webm"
