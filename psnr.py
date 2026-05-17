# Пиковое отношение сигнала к шуму (англ. peak signal-to-noise ratio)
# обозначается аббревиатурой PSNR и является инженерным термином,
# означающим соотношение между максимумом возможного значения сигнала и
# мощностью шума, искажающего значения сигнала.

from math import log10, sqrt
import cv2
import numpy as np
from pathlib import Path


def PSNR(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    if (mse == 0):  # MSE is zero means no noise is present in the signal .
        # Therefore PSNR have no importance.
        return 100
    max_pixel = 255.0
    psnr = 20 * log10(max_pixel / sqrt(mse))
    return psnr


folder_path = Path('./contrast_embed_result/Set3')
original_base = Path('./Set3')   # путь к папке с оригиналами

for file in folder_path.iterdir():
    if file.is_file() and file.suffix.lower() in {'.bmp'}:
        compressed_path = str(file)
        original_filename = file.name.replace("_watermarked", "")
        original_path = original_base / original_filename

        # Проверяем, существует ли оригинал
        if not original_path.exists():
            print(f"Оригинал не найден: {original_path}, пропускаем {original_filename}")
            continue

        # Читаем изображения в оттенках серого (флаг 1 = CV_LOAD_IMAGE_COLOR, но для PSNR лучше grayscale)
        original = cv2.imread(str(original_path), cv2.IMREAD_GRAYSCALE)
        compressed = cv2.imread(compressed_path, cv2.IMREAD_GRAYSCALE)

        if original is None or compressed is None:
            print(f"Ошибка чтения {file.name}")
            continue

        psnr_val = PSNR(original, compressed)
        print(f"{psnr_val:.2f} dB")

