import argparse

from src.config.app_config import get_config
from src.config.logging_config import load_logger_config
from src.utils import open_settings
from src.scripts import download_audio


def main():
    # Надо где-то объявить, вот объявил.
    config = get_config()
    load_logger_config(debug_mode=config.extended.debug_mode)

    # Создаем парсер для аргументов командной строки
    parser = argparse.ArgumentParser(
        description=(
            "YouTube Audio Downloader\n\n"
            "This tool allows you to download audio from YouTube videos, playlists, or \n"
            "channels. You can specify the URL of a video, playlist, or channel, and the \n"
            "downloaded audio will be saved to the path you provide.\n\n"
            "Configuration settings can be defined in a configuration file.\n\n"
            "Examples of usage:\n"
            "  # Download audio from a video (Limit 10000 API requests/day)\n"
            "  ./run.sh https://www.youtube.com/watch?v=6OaTvs07k5U\n\n"
            "  # Download audio from a playlist (Limit 10000 API requests/day)\n"
            "  ./run.sh https://youtube.com/playlist?list=PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG\n\n"
            "  # Download audio from a channel (Limit 100 API requests/day)\n"
            "  ./run.sh https://www.youtube.com/@808nation\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter  # Сохраняет форматирование текста
    )

    # Добавляем аргумент для URL видео, плейлиста или канала
    parser.add_argument(
        'url',
        type=str,
        nargs='?',
        help="URL of the YouTube video, playlist, or channel to download."
    )

    # Добавляем аргумент для открытия файла конфигурации
    parser.add_argument(
        '-s', '--settings',
        action='store_true',
        help="Open the .env file in the default console editor."
    )

    # Разбираем аргументы
    args = parser.parse_args()

    # Если указан флаг -s, открываем файл .env
    if args.settings:
        open_settings()
    elif args.url:
        # Вызываем функцию для загрузки аудио
        download_audio(args.url)
    else:
        parser.print_help()


def backdoor(url: str):
    """Для запуска из кода"""
    config = get_config()
    load_logger_config(debug_mode=config.extended.debug_mode)
    download_audio(url)


if __name__ == '__main__':
    main()
