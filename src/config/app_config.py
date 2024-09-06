from dataclasses import dataclass
from environs import Env
from threading import Lock


@dataclass
class Api:
    yt_token: str


@dataclass
class Settings:
    write_thumbnail: bool
    write_metadata: bool
    audio_codec: str
    audio_ext: str
    thumbnail_resize: bool
    thumbnail_max_width: int
    download_directory: str
    debug_mode: bool


@dataclass
class Config:
    api: Api
    settings: Settings


class ConfigManager:
    _instance: Config = None
    _lock: Lock = Lock()

    @classmethod
    def load_config(cls, env_file: str) -> Config:
        with cls._lock:
            if cls._instance is None:
                env = Env()
                env.read_env(env_file)
                cls._instance = Config(
                    api=Api(
                        yt_token=env("API_KEY_YOUTUBE")
                    ),
                    settings=Settings(
                        write_thumbnail=env.bool("WRITE_THUMBNAIL", True),
                        write_metadata=env.bool("WRITE_METADATA", True),
                        audio_codec=env.str("AUDIO_CODEC", "opus"),
                        audio_ext=env.str("AUDUO_EXT", "opus"),
                        thumbnail_resize=env.bool("THUMBNAIL_RESIZE", True),
                        thumbnail_max_width=env.int("THUMBNAIL_MAX_WIDTH", 300),
                        download_directory=env.str("DOWNLOAD_DIRECTORY", ""),
                        debug_mode=env.bool("DEBUG_MODE", False)
                    )
                )
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
