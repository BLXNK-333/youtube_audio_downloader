import os
import logging
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TIT2, TPE1, TDRC, COMM

from ..entities import Metadata


class MetadataHandler:
    _ext_hmap = {'.opus': OggOpus, '.m4a': MP4, '.mp3': ID3}

    def __init__(self):
        self._yt_dlp_logger = logging.getLogger('yt-dlp')

    def add_metadata(self, filepath: str, metadata: Metadata) -> None:
        _, ext = os.path.splitext(filepath)
        audio = MetadataHandler._ext_hmap[ext](filepath)

        if isinstance(audio, OggOpus):
            audio['title'] = metadata.title
            audio['artist'] = metadata.artist
            audio['date'] = metadata.date
            audio['comment'] = metadata.comment
        elif isinstance(audio, MP4):
            audio['\xa9nam'] = metadata.title
            audio['\xa9ART'] = metadata.artist
            audio['\xa9day'] = metadata.date
            audio['\xa9cmt'] = metadata.comment
        elif isinstance(audio, ID3):
            audio.add(TIT2(encoding=3, text=metadata.title))
            audio.add(TPE1(encoding=3, text=metadata.artist))
            audio.add(TDRC(encoding=3, text=metadata.date))
            audio.add(COMM(encoding=3, text=metadata.comment))

        audio.save()
        self._yt_dlp_logger.info("[*convertor] Metadata added successfully")
