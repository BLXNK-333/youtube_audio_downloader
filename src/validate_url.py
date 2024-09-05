from enum import StrEnum


class Entity(StrEnum):
    VIDEO = "VIDEO"
    PLAYLIST = "PLAYLIST"
    BAD_LINK = "BAD_LINK"


class UrlPrefix(StrEnum):
    VIDEO = "https://www.youtube.com/watch?v="
    PLAYLIST = "https://www.youtube.com/playlist?list="
    SHARE = "https://youtu.be/"


def what_entity(url: str) -> str:
    if url.startswith(UrlPrefix.PLAYLIST):
        return Entity.PLAYLIST
    if url.startswith(UrlPrefix.VIDEO) or url.startswith(UrlPrefix.SHARE):
        return Entity.VIDEO

    return Entity.BAD_LINK


def extract_id_from_url(url: str):
    pass