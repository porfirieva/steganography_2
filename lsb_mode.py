# Внедрение цифрового водяного знака (логотипа) в изображение-контейнер методом LSB
# Пользователь выбирает:
# - изображение-контейнер
# - изображение-логотип (ЦВЗ)
# Выходное изображение сохраняется как 8-битное серое
# Результат сохранен по пути /lsb_embed_result/Set{set_number}/{result}

from PIL import Image
from pathlib import Path
import random
from constants import SET_MESSAGE


def embed_lsb_keyed(container_path, watermark_path, output_path, key):
    container = Image.open(container_path).convert('L')
    watermark = Image.open(watermark_path).convert('L')

    # Получаем размеры
    width, height = container.size
    pixels = container.load()

    # Получаем биты водяного знака
    watermark_width, watermark_height = watermark.size
    watermark_pixels = watermark.load()

    # Формируем массив битов водяного знака
    watermark_bits = []
    for y in range(watermark_height):
        for x in range(watermark_width):
            pixel = watermark_pixels[x, y]
            binary_pixel = format(pixel, '08b')
            for bit in binary_pixel:
                watermark_bits.append(int(bit))

    total_pixels = width * height
    bits_to_write = min(len(watermark_bits), total_pixels)

    # Генерируем псевдослучайную последовательность координат с использованием секретного ключа
    random.seed(key)

    # Создаем список всех позиций пикселей
    positions = [(x, y) for y in range(height) for x in range(width)]
    random.shuffle(positions)

    written = 0
    # Встраиваем биты в случайном порядке
    for x, y in positions:
        if written >= bits_to_write:
            break
        pixel = pixels[x, y]
        new_pixel = (pixel & 0xFE) | watermark_bits[written]
        pixels[x, y] = new_pixel
        written += 1

    # Сохраняем результат
    container.save(output_path)
    return written, len(watermark_bits)


def main():
    print("Программа встраивания цифрового водяного знака (логотипа) методом LSB с секретным ключом (псевдослучайный порядок)")

    set_number = input(SET_MESSAGE)
    folder_path = Path('./' + 'Set' + set_number)

    print('Используется режим встраивания ЦВЗ: ./watermark.bmp')
    watermark_path = './watermark.bmp'

    key = int(input("Введите секретный ключ (число): "))
    for file in folder_path.iterdir():
        output_folder = Path(f"./lsb_embed_result/Set{set_number}/")
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = output_folder / f"{file.stem}_watermarked.bmp"

        # Встраивание
        print("\nВстраивание водяного знака...")
        embedded, total = embed_lsb_keyed(file, watermark_path, output_path, key)
        print(f"Режим: LSB с секретным ключом (key={key})")

        # Размеры контейнера для отчета
        container = Image.open(file).convert('L')
        container_capacity = container.width * container.height

        print(f"\nРезультат:")
        print(f"  Размер контейнера: {container.width}x{container.height} = {container_capacity} пикселей")
        print(f"  Размер ЦВЗ: {total} бит")
        print(f"  Встроено бит: {embedded}")
        print(f"  Процент заполнения: {embedded / container_capacity * 100:.1f}%")
        print(f"  Сохранено: {output_path}")


if __name__ == "__main__":
    main()