from ..config.app_config import get_config
from ..entities import Metadata
from .audio_converter import AudioConverter
from .image_embedder import ImageEmbedder
from .metadata_handler import MetadataHandler


class Converter:
    def __init__(self):
        self._config = get_config()
        self._audio_converter = AudioConverter()
        self._image_embedder = ImageEmbedder()
        self._metadata_handler = MetadataHandler()

    def convert(self, audio_path: str, cover_path: str, metadata: Metadata) -> None:
        converted_audio = self._audio_converter.convert_audio(audio_path)

        if self._config.download.write_thumbnail:
            self._image_embedder.embed_image(converted_audio, cover_path)

        if self._config.download.write_metadata:
            self._metadata_handler.add_metadata(converted_audio, metadata)
