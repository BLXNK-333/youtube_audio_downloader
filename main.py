import argparse
from src import (
    get_config,
    load_logger_config,
    download_audio
)


def main():
    # Надо где-то объявить, вот объявил.
    config = get_config()
    load_logger_config(debug_mode=config.settings.debug_mode)

    # Создаем парсер для аргументов командной строки
    parser = argparse.ArgumentParser(
        description=(
            "YouTube Audio Downloader\n\n"
            "This tool allows you to download audio from YouTube videos or playlists.\n"
            "You can specify the URL of a video or playlist, and the downloaded audio "
            "will be saved to the path you provide.\n\n"
            "Configuration settings can be defined in a configuration file."
        )
    )

    # Добавляем аргумент для URL видео или плейлиста
    parser.add_argument(
        'url',
        type=str,
        help="URL of the YouTube video or playlist to download."
    )

    # Разбираем аргументы
    args = parser.parse_args()

    # Вызываем функцию для загрузки аудио
    download_audio(args.url)


def get(url):
    config = get_config()
    load_logger_config(debug_mode=config.settings.debug_mode)
    download_audio(url)


if __name__ == '__main__':
    # main()
    get("https://www.youtube.com/playlist?list=PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG")