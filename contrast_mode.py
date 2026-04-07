# # В областях с высоким контрастом (резкие перепады яркости) встраиваем в большее количество бит, в гладких областях - в меньшее.
# # Внедрение цифрового водяного знака (логотипа) в изображение-контейнер методом адаптации по локальному контрасту (вариант 3)
# # Пользователь выбирает:
# # - изображение-контейнер
# # - изображение-логотип (ЦВЗ)
# # Выходное изображение сохраняется как 8-битное серое
# # Результат сохранен по пути /contrast_embed_result/Set{set_number}/{result}
#
# # Количество встраиваемых бит зависит от контраста:
# # Контраст < 0.1 (гладкие области): 1 бит
# # Контраст 0.1-0.3: 2 бита
# # Контраст 0.3-0.6: 3 бита
# # Контраст > 0.6: до 4 бит
#
# # В отличие от существующих алгоритмов, предлагаемый подход опирается на предварительную сегментацию изображения на зоны с последующим
# # подбором параметров кривой контраста для каждой зоны в
# # отдельности, что позволяет учесть наличие недоэкспонированных
# # и переэкспонированных участков. Для обеспечения равномерности
# # переходов между зонами предлагается согласовывать параметры
# # соседних зон с помощью построения графа параметров алгоритма
# # специального вида.

# Также сохраняем маску встраивания с информацией о том, сколько бит в какой пиксель встроено
# /contrast_embed_result/Set{set_number}/{result}.mask.json

from PIL import Image
from pathlib import Path
import random
import json
from constants import SET_MESSAGE

def calculate_local_contrast(pixels, x, y, width, height):
    """Вычисляет локальный контраст в окне 3x3"""
    neighbors = []
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                neighbors.append(pixels[nx, ny])

    if not neighbors:
        return 0

    min_val = min(neighbors)
    max_val = max(neighbors)

    if max_val + min_val == 0:
        return 0

    contrast = (max_val - min_val) / (max_val + min_val + 1e-6)
    return contrast


def get_adaptive_bits_per_pixel(contrast):
    """Определяет количество бит для встраивания в пиксель на основе контраста"""
    if contrast < 0.1:  # Гладкая область
        return 1
    elif contrast < 0.3:  # Средний контраст
        return 2
    elif contrast < 0.6:  # Высокий контраст
        return 3
    else:  # Очень высокий контраст
        return 4


def embed_contrast(container_path, watermark_path, output_path, key):
    container = Image.open(container_path).convert('L')
    watermark = Image.open(watermark_path).convert('L')

    width, height = container.size
    pixels = container.load()

    watermark_width, watermark_height = watermark.size
    watermark_pixels = watermark.load()

    # Формируем биты водяного знака
    watermark_bits = []
    for y in range(watermark_height):
        for x in range(watermark_width):
            pixel = watermark_pixels[x, y]
            binary_pixel = format(pixel, '08b')
            for bit in binary_pixel:
                watermark_bits.append(int(bit))

    total_watermark_bits = len(watermark_bits)

    print(f"Всего бит ЦВЗ: {total_watermark_bits}")

    # Вычисляем контраст для каждого пикселя и сохраняем маску
    random.seed(key)

    pixel_info = []
    mask = [[0 for _ in range(width)] for _ in range(height)]  # Маска для сохранения
    total_pixels = width * height
    step = total_pixels // 10

    for i, y in enumerate(range(height)):
        for x in range(width):
            contrast = calculate_local_contrast(pixels, x, y, width, height)
            bits_to_embed = get_adaptive_bits_per_pixel(contrast)
            pixel_info.append((x, y, bits_to_embed))
            mask[y][x] = bits_to_embed  # Сохраняем в маску

        if (i * width) % step == 0 and i > 0:
            percent = (i * width) / total_pixels * 100
            print(f"    Прогресс: {percent:.1f}%")

    # Перемешивание с использованием ключа
    random.shuffle(pixel_info)

    # Сохраняем маску и порядок пикселей для извлечения
    mask_path = output_path.with_suffix('.mask.json')
    with open(mask_path, 'w') as f:
        json.dump({
            'mask': mask,
            'width': width,
            'height': height,
            'total_bits': total_watermark_bits,
            'key': key
        }, f)
    print(f"Маска сохранена: {mask_path}")

    bit_index = 0
    written = 0
    for x, y, bits_to_embed in pixel_info:
        if bit_index >= total_watermark_bits:
            break
        pixel = pixels[x, y]
        new_pixel = pixel

        for b in range(bits_to_embed):
            if bit_index + b < total_watermark_bits:
                bit_value = watermark_bits[bit_index + b]
                new_pixel = (new_pixel & ~(1 << b)) | (bit_value << b)

        pixels[x, y] = new_pixel
        bit_index += bits_to_embed
        written += bits_to_embed

    print(f"Сохранено в {output_path}")
    container.save(output_path)

    return written, total_watermark_bits


def main():
    print("Программа адаптивного встраивания цифрового водяного знака (логотипа) по локальному контрасту")

    set_number = input(SET_MESSAGE)
    folder_path = Path('./' + 'Set' + set_number)

    print('Используется режим встраивания ЦВЗ: ./watermark.bmp')
    watermark_path = './watermark.bmp'

    key = int(input("Введите секретный ключ (число): "))

    for file in folder_path.iterdir():
        print(f"Обработка {file.name}")

        output_folder = Path(f"./contrast_embed_result/Set{set_number}/")
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = output_folder / f"{file.stem}_watermarked.bmp"

        embedded, total = embed_contrast(file, watermark_path, output_path, key)
        container = Image.open(file).convert('L')
        container_capacity = container.width * container.height

        print(f"Размер контейнера {container_capacity} пикселей")
        print(f"Размер ЦВЗ: {total} бит")
        print(f"Встроено бит: {embedded}")
        print(f"Процент заполнения: {embedded / container_capacity * 100:.1f}%")
        print(f"Сохранено: {output_path}")

if __name__ == "__main__":
    main()