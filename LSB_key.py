# Внедрение ЦВЗ в LSB с порядком по секретному ключу

from PIL import Image
import numpy as np
import random
from pathlib import Path

from constants import SET_MESSAGE


def embed_watermark(container_path, watermark_path, key, output_path):
    container = Image.open(container_path).convert('L')
    pixels = np.array(container)

    watermark = Image.open(watermark_path).convert('1')
    watermark_data = np.array(watermark).flatten()

    watermark_bits = (watermark_data > 0).astype(int)

    total_pixels = pixels.size
    required_bits = len(watermark_bits)

    if required_bits > total_pixels // 2:
        print(f"Предупреждение: ЦВЗ слишком большой")
        print(f"Требуется бит: {required_bits}")
        print(f"Максимум (50% емкости): {total_pixels // 2}")
        print(f"Будет встроено только {total_pixels // 2}")
        watermark_bits = watermark_bits[:total_pixels // 2]
    elif required_bits < total_pixels // 2:
        print(f"Объем ЦВЗ: {required_bits} бит")
        print(f"Требование (50% емкости): {total_pixels // 2} бит")
        exit()

    # Генерируем порядок внедрения по ключу
    random.seed(key)
    indices = list(range(total_pixels))
    random.shuffle(indices)

    # Встраиваем биты в LSB выбранных пикселей
    pixels_flat = pixels.flatten()

    for i, bit in enumerate(watermark_bits):
        idx = indices[i]
        # Обнуляем LSB и устанавливаем новый бит
        pixels_flat[idx] = (pixels_flat[idx] & 0xFE) | bit

    # Сохраняем результат
    result = Image.fromarray(pixels_flat.reshape(pixels.shape))
    result.save(output_path)

    print(f"Встроено бит: {len(watermark_bits)}")
    print(f"Сохранено: {output_path}")

    return len(watermark_bits)


def extract_watermark(stego_path, output_path, key, original_shape=None):
    """
    Извлечение водяного знака из изображения

    Параметры:
        stego_path: путь к изображению со встроенным ЦВЗ
        key: секретный ключ (тот же, что при внедрении)
        output_path: путь для сохранения извлеченного ЦВЗ
        original_shape: размер исходного ЦВЗ (height, width)
    """
    # Загружаем изображение
    stego = Image.open(stego_path).convert('L')
    pixels = np.array(stego).flatten()
    total_pixels = len(pixels)

    # Генерируем тот же порядок
    random.seed(key)
    indices = list(range(total_pixels))
    random.shuffle(indices)

    # Извлекаем биты (первые total_pixels//2 бит)
    extracted_bits = []
    for i in range(total_pixels // 2):
        idx = indices[i]
        extracted_bits.append(pixels[idx] & 1)

    # Если знаем размер, восстанавливаем изображение
    if original_shape:
        watermark_array = np.array(extracted_bits[:original_shape[0] * original_shape[1]])
        watermark_array = watermark_array.reshape(original_shape) * 255
        result = Image.fromarray(watermark_array.astype(np.uint8))
    else:
        # Иначе сохраняем как есть
        result = Image.fromarray(np.array(extracted_bits).astype(np.uint8) * 255)

    result.save(output_path)
    print(f"Извлечено бит: {len(extracted_bits)}")
    print(f"Сохранено: {output_path}")


def main():
    mode = input('Выберите режим работы с изображением: 1 - Встраивание, 2 - Извлечение: ')
    set_number = input(SET_MESSAGE)
    key = int(input("Введите секретный ключ (число): "))
    watermark = './watermark.bmp'

    if mode == '1':
        print('Используется режим встраивания ЦВЗ: ./watermark.bmp')

        folder_path = Path('./' + 'Set' + set_number)
        output_folder = Path(f"./lsb_embed_result/Set{set_number}/")
        output_folder.mkdir(parents=True, exist_ok=True)

        for file in folder_path.iterdir():
            output_path = output_folder / f"{file.stem}_watermarked.bmp"
            embed_watermark(file, watermark, key, output_path)

    elif mode == '2':
        print('Используется режим извлечения ЦВЗ: ./watermark.bmp')

    else:
        print('Некорректный режим')



if __name__ == "__main__":
    main()