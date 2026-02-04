import shutil
from pathlib import Path


def read_filenames_from_file(file_path: str):
    """Читает список названий файлов из файла и возвращает как множество"""
    with open(file_path, 'r') as f:
        filenames = {line.strip() for line in f.readlines()}
    return filenames


def move_files_not_in_list(source_folder: Path, target_folder: Path, known_files_file: str):
    """Перемещает файлы, названия которых нет в списке известных"""
    if not target_folder.exists():
        target_folder.mkdir(parents=True)

    # Читаем список известных названий файлов (без расширений)
    known_filenames = read_filenames_from_file(known_files_file)

    # Проходим по всем файлам в исходной папке
    for file_path in source_folder.rglob('*'):
        if file_path.is_file():
            # Получаем название файла без расширения
            file_name_without_ext = file_path.stem
            if file_name_without_ext in known_filenames:
                # Если название файла не в списке - перемещаем файл
                target_path = target_folder / file_path.name
                shutil.move(str(file_path), str(target_path))


if __name__ == '__main__':
    source_folder = Path('/home/blxnk/Downloads/YouTube/The Void 2016/')
    target_folder = Path('/home/blxnk/Downloads/YouTube/The Void unadded/')
    known_files_file = '/home/blxnk/Downloads/123.txt'

    move_files_not_in_list(source_folder, target_folder, known_files_file)
