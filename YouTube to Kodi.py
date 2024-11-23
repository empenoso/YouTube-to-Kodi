# ==============================================================================
# Project Name:        YouTube to Kodi
# Repository:          https://github.com/empenoso/YouTube-to-Kodi/
# Author:              Mikhail Shardin, https://shardin.name/
# Created Date:        2024-11-23
# Last Modified Date:  2024-11-23
# Description:         https://habr.com/ru/articles/860706/
# Version:             1.0
# License:             Apache 2.0
# ==============================================================================

import sys
import os
import subprocess
import json
import requests

sys.stdout.reconfigure(encoding="utf-8")


def download_video(url, output_dir, cookies_file):
    # Путь для выходного видеофайла
    output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

    # Команда yt-dlp для загрузки видео с использованием cookies
    command = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio/best",  # Выбор лучшего видео и аудио
        "--merge-output-format", "mkv",    # Сохранение в MKV
        "-o", output_template,            # Шаблон имени файла
        "--write-info-json",              # Сохранение метаданных
        "--cookies", cookies_file,        # Передача cookies для аутентификации
        url
    ]

    print("Загружается видео...")
    subprocess.run(command, check=True)
    print("Видео успешно загружено.")

    # Находим JSON файл с метаданными
    info_json_path = next(
        (os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".info.json")), None
    )
    if not info_json_path:
        raise FileNotFoundError("Файл метаданных .info.json не найден.")

    return info_json_path


def create_kodi_friendly_files(info_json_path):
    # Читаем данные из JSON файла
    with open(info_json_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    title = metadata.get("title", "Без названия")
    description = metadata.get("description", "Нет описания")
    thumbnail = metadata.get("thumbnail", "")

    # Путь к базовым файлам (без расширений)
    base_path = os.path.splitext(info_json_path)[0].replace(".info", "")

    # Загружаем обложку, если доступна
    cover_path = f"{base_path}-fanart.jpg"
    if thumbnail:
        with open(cover_path, "wb") as f:
            f.write(requests.get(thumbnail).content)
        print(f"Обложка сохранена: {cover_path}")
    else:
        print("Обложка не найдена.")

    # Создаем содержимое .nfo файла
    nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>{title}</title>
    <plot>{description}</plot>
    <thumb>{cover_path}</thumb>
</movie>
"""

    # Сохраняем .nfo файл
    nfo_path = f"{base_path}.nfo"
    with open(nfo_path, "w", encoding="utf-8") as nfo_file:
        nfo_file.write(nfo_content)

    print(f".nfo файл успешно создан: {nfo_path}")


# Основная программа
def main():
    url = "https://www.youtube.com/watch?v=_lvcEUi1MtE"
    output_dir = "./downloads"
    cookies_file = "./cookies.txt"  # Укажите путь к файлу cookies

    os.makedirs(output_dir, exist_ok=True)

    try:
        info_json_path = download_video(url, output_dir, cookies_file)
        create_kodi_friendly_files(info_json_path)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()