from typing import Optional
from dataclasses import dataclass
from environs import Env
from threading import Lock


@dataclass
class Api:
    yt_token: str
    endpoint: str


@dataclass
class Download:
    write_thumbnail: bool
    write_metadata: bool
    audio_ext: str
    thumbnail_resize: bool
    thumbnail_max_width: int
    download_directory: str
    filename_format: str
    skip_shorts: bool


@dataclass
class Extended:
    debug_mode: bool
    filter_date: str


@dataclass
class Config:
    api: Api
    download: Download
    extended: Extended


class ConfigManager:
    _instance: Optional[Config] = None
    _lock: Lock = Lock()

    @classmethod
    def __create_config(cls, env: Env) -> None:
        cls._instance = Config(
            api=Api(
                yt_token=env.str("API_KEY_YOUTUBE"),
                endpoint=env.str("ENDPOINT")
            ),
            download=Download(
                write_thumbnail=env.bool("WRITE_THUMBNAIL", True),
                write_metadata=env.bool("WRITE_METADATA", True),
                audio_ext=env.str("AUDIO_EXT") or "",
                thumbnail_resize=env.bool("THUMBNAIL_RESIZE", False),
                thumbnail_max_width=env.int("THUMBNAIL_MAX_WIDTH", 350),
                download_directory=env.str("DOWNLOAD_DIRECTORY") or "YouTube",
                filename_format=env.str("FILENAME_FORMAT") or "%(title)s.%(ext)s",
                skip_shorts=env.bool("SKIP_SHORTS", True)
            ),
            extended=Extended(
                debug_mode=env.bool("DEBUG_MODE", False),
                filter_date=env.str("FILTER_DATE") or ""
            )
        )

    @classmethod
    def load_config(cls, env_file: str) -> Config:
        with cls._lock:
            if cls._instance is None:
                env = Env()
                env.read_env(env_file)
                cls.__create_config(env)

            assert cls._instance is not None
            return cls._instance


# Функция для получения текущей конфигурации
def get_config(env_file: str = ".env") -> Config:
    """
    При вызове возвращает ссылку на один и тот же объект конфигурации,
    реализован singleton.

    :param env_file: (str) Путь до файла ".env", необязательный параметр.
    :return: (Config)
    """
    return ConfigManager.load_config(env_file)
