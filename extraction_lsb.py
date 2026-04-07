# Извлечение цифрового водяного знака (логотипа) из изображения-контейнера методом LSB
# Пользователь выбирает:
# - изображение с внедренным ЦВЗ
# - секретный ключ (для восстановления порядка пикселей)
# Выходное изображение сохраняется как 8-битное серое
# Результат сохранен по пути /lsb_extract_result/Set{set_number}/{result}

from PIL import Image
from pathlib import Path
import random
from constants import SET_MESSAGE


def extract(container_path, output_path, key, original_watermark_size):
    container = Image.open(container_path).convert('L')

    # Получаем размеры
    width, height = container.size
    pixels = container.load()

    total_pixels = width * height

    # Генерируем ту же псевдослучайную последовательность координат с использованием секретного ключа
    random.seed(key)

    # Создаем список всех позиций пикселей (в том же порядке, что и при встраивании)
    positions = [(x, y) for y in range(height) for x in range(width)]
    random.shuffle(positions)

    # Извлекаем LSB биты в том же порядке
    extracted_bits = []
    bits_to_extract = min(original_watermark_size, total_pixels)

    for i in range(bits_to_extract):
        x, y = positions[i]
        pixel = pixels[x, y]
        # Извлекаем LSB (младший бит)
        extracted_bit = pixel & 1
        extracted_bits.append(extracted_bit)

    # Преобразуем биты обратно в пиксели (по 8 бит на пиксель)
    watermark_pixels = []
    for i in range(0, len(extracted_bits), 8):
        if i + 8 <= len(extracted_bits):
            byte_bits = ''.join(str(bit) for bit in extracted_bits[i:i + 8])
            watermark_pixels.append(int(byte_bits, 2))

    # Вычисляем размеры изображения ЦВЗ (исходим из количества пикселей)
    watermark_size = int((len(watermark_pixels)) ** 0.5)
    # Если квадрат не получается, корректируем размер
    while watermark_size * watermark_size < len(watermark_pixels):
        watermark_size += 1

    # Создаем изображение ЦВЗ
    watermark_image = Image.new('L', (watermark_size, watermark_size), 255)
    watermark_image.putdata(watermark_pixels[:watermark_size * watermark_size])

    # Сохраняем результат
    watermark_image.save(output_path)

    return len(extracted_bits), len(watermark_pixels), watermark_size


def main():
    print(
        "Программа извлечения цифрового водяного знака (логотипа) методом LSB с секретным ключом (псевдослучайный порядок)")

    set_number = input(SET_MESSAGE)
    folder_path = Path('./lsb_embed_result/Set' + set_number)

    key = int(input("Введите секретный ключ (число): "))
    original_watermark_size = int(input("Введите размер исходного ЦВЗ в битах (из лога встраивания): "))

    for file in folder_path.iterdir():
        output_folder = Path(f"./lsb_extract_result/Set{set_number}/")
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = output_folder / f"{file.stem}_extracted.bmp"

        # Извлечение
        print("\nИзвлечение водяного знака...")
        extracted_bits, pixel_count, wm_size = extract(file, output_path, key, original_watermark_size)
        print(f"Режим: LSB с секретным ключом (key={key})")

        # Размеры контейнера для отчета
        container = Image.open(file).convert('L')
        container_capacity = container.width * container.height

        print(f"\nРезультат:")
        print(f"  Размер контейнера: {container.width}x{container.height} = {container_capacity} пикселей")
        print(f"  Извлечено бит: {extracted_bits}")
        print(f"  Размер извлеченного ЦВЗ: {pixel_count} пикселей")
        print(f"  Размер изображения ЦВЗ: {wm_size}x{wm_size}")
        print(f"  Сохранено: {output_path}")


if __name__ == "__main__":
    main()