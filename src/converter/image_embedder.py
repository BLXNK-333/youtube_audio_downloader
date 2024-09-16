import os
import logging
from io import BytesIO
from base64 import b64encode

from PIL import Image
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import Picture
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC
from mutagen.id3._util import error as ID3Error

from ..config.app_config import get_config


class ImageEmbedder:
    def __init__(self):
        self._config = get_config()
        self._resize = self._config.download.thumbnail_resize
        self._max_width = self._config.download.thumbnail_max_width
        self._yt_dlp_logger = logging.getLogger('yt-dlp')

    def _convert_image(self, image_path: str) -> BytesIO:
        with Image.open(image_path) as img:
            if self._resize:
                img.thumbnail((self._max_width, self._max_width),
                              Image.Resampling.LANCZOS)
                self._yt_dlp_logger.debug(
                    f"[*convertor] Resized image {image_path} to {self._max_width}px")

            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='WEBP')
            img_byte_arr.seek(0)
            return img_byte_arr

    def _embed_oggopus_cover(self, audio_path: str, img_stream: BytesIO):
        covart = Picture()
        covart.data = img_stream.read()
        covart.type = 3  # Cover (front)
        covart.mime = 'image/png'

        audio = OggOpus(audio_path)
        audio['METADATA_BLOCK_PICTURE'] = b64encode(covart.write()).decode('ascii')
        audio.save()

    def _embed_mp4_cover(self, audio_path: str, img_stream: BytesIO):
        audio = MP4(audio_path)
        cover_data = img_stream.read()

        audio['covr'] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_PNG)]
        audio.save()

    def _embed_mp3_cover(self, audio_path: str, img_stream: BytesIO):
        cover_data = img_stream.read()
        try:
            audio = ID3(audio_path)
        except ID3Error:
            # Если ID3-тегов еще нет, создадим их
            audio = ID3()

        audio.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/png',
                type=3,  # Cover (front)
                desc='Cover',
                data=cover_data
            )
        )
        audio.save(audio_path)

    def embed_image(self, audio_path: str, image_path: str) -> None:
        img_stream = self._convert_image(image_path)
        ext = os.path.splitext(audio_path)[1].lower()

        _metadata_map = {
            ".opus": self._embed_oggopus_cover,
            ".m4a": self._embed_mp4_cover,
            ".mp3": self._embed_mp3_cover
        }

        if ext not in _metadata_map:
            self._yt_dlp_logger.error(f"[*convertor] Unsupported audio format: {ext}")
            return

        metadata_handler = _metadata_map[ext]
        metadata_handler(audio_path, img_stream)
        self._yt_dlp_logger.info(f"[*convertor] Thumbnail added successfully")
