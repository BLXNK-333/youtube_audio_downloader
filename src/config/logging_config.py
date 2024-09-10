import sys
import logging.config
import coloredlogs


logging_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] "
                      "#%(levelname)-8s "
                      "%(filename)s:%(lineno)d - %(name)s:%(funcName)s - %(message)s"
        },
        "easy": {
            "format": "[%(asctime)s] #%(levelname)-8s - %(message)s"
        },
        "indented": {
            "format": "   %(message)s"  # Формат с отступом для yt-dlp
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",  # Применяем формат easy для stdout
            "stream": sys.stdout
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "default",  # Применяем формат easy для stderr
            "stream": sys.stderr
        },
        "yt_dlp_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "indented",  # Применяем формат с отступом для yt-dlp
            "stream": sys.stdout
        }
    },
    "loggers": {
        "yt-dlp": {
            "handlers": ["yt_dlp_handler"],
            "level": "DEBUG",
            "propagate": False
        }
    },
    "root": {
        "level": "DEBUG",
        "formatter": "default",  # Используем формат default для root
        "handlers": ["stdout"]
    }
}


def load_logger_config(debug_mode: bool = False):
    # Применяем конфигурацию логирования
    if debug_mode:
        logging_config["root"]["level"] = "DEBUG"
        logging_config["handlers"]["stdout"]["formatter"] = "default"
    else:
        logging_config["root"]["level"] = "INFO"
        logging_config["handlers"]["stdout"]["formatter"] = "easy"

    logging.config.dictConfig(logging_config)

    # Устанавливаем цветное форматирование для корневого логгера
    coloredlogs.install(
        level=logging_config["root"]["level"],
        fmt=
        logging_config['formatters'][logging_config["handlers"]["stdout"]["formatter"]][
            'format'],
        logger=logging.getLogger()  # Применяем ко всему
    )
