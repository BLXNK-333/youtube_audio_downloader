import re
from .entities import YoutubeLink


def extract_type_and_id(url: str):
    video_pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    playlist_pattern = r"(?:list=)([0-9A-Za-z_-]{13,})"

    video_match = re.search(video_pattern, url)
    playlist_match = re.search(playlist_pattern, url)

    if video_match:
        return YoutubeLink.VIDEO, video_match.group(1)
    elif playlist_match:
        return YoutubeLink.PLAYLIST, playlist_match.group(1)
    else:
        return YoutubeLink.BAD_LINK, ""
