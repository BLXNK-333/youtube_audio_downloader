import logging
import re

from .entities import AudioExt

logger = logging.getLogger()


def validate_audio_format(output_format: str) -> bool:
    """
    Проверяет формат заданный в настройках, если передан неподдерживаемый,
    отправляет в stdout сообщение об ошибке.

    :param output_format: (str) формат AUDIO_EXT из настроек.
    :return: (bool) True, если поддерживается, иначе False.
    """

    supported_formats = {AudioExt.OGG, AudioExt.M4A, AudioExt.MP3, AudioExt.BEST_}
    if output_format not in supported_formats:
        logger.error(
            f"\n End audio container not supported: {output_format}\n"
            f" Use AUDIO_EXT=[{'|'.join(supported_formats)}] in settings")
        return False
    return True


def validate_date_filter(filter_expression: str) -> bool:
    """
    Проверяет на валидность фильтр (FILTER_DATE) из настроек.

    :param filter_expression: (str) Фильтр - логическое выражение.
    :return: (bool) True, если фильтр пройден, иначе False
    """
    if filter_expression == "":
        return True

    allowed_characters = "0123456789x(){}[],!<>=orandti"
    allowed_hashset = set(allowed_characters)
    filter_str = re.sub(r"[\[\]\s]", "", filter_expression).lower()

    tip_param = 'TIP: Edit the FILTER_DATE parameter in the settings or set it to "".'
    tip_allowed = f"TIP: List of allowed characters: {allowed_characters}"

    if len(filter_expression) > 100:
        logger.error(
            f"\n The filter length should not exceed 100 characters."
            f"\n {tip_param}")
        return False

    if not all(ch in allowed_hashset for ch in filter_str):
        logger.error(
            f"\n The filter contains invalid characters"
            f"\n {tip_allowed}"
            f"\n {tip_param}"
        )
        return False

    try:
        filter_expression = filter_str.replace("x", "2020")
        eval(filter_expression)
        return True
    except (SyntaxError, NameError, TypeError, ValueError) as e:
        logger.error(
            f"\n Expression parsing error: {filter_expression}, {e}"
            f"\n TIP: Use boolean expression syntax for Python's eval function. "
            f"\n  Example: 2017 < [x] <= 2024"
            f"\n  Example: [x] == 2024"
            f"\n  Example: [x] in {2017, 2019, 2023}"
            f"\n  Example: ([x] <= 2017) or ([x] >= 2020)"
            f"\n {tip_allowed}"
            f"\n {tip_param}")
        return False
