#!/bin/bash

# Определяем путь до директории скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Путь до интерпретатора и скрипта
VENV_PATH="$SCRIPT_DIR/.venv"
PY_SCRIPT_PATH="$SCRIPT_DIR/main.py"

# Переходим в директорию скрипта
cd "$SCRIPT_DIR" || exit

# Активация виртуального окружения
source "$VENV_PATH/bin/activate"

# Запуск Python-скрипта
python3 "$PY_SCRIPT_PATH" "$@"

# Деактивация виртуального окружения
deactivate
