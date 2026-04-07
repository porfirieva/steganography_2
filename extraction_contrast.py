# # Извлечение цифрового водяного знака (логотипа) из изображения-контейнера
# # методом адаптации по локальному контрасту
# # Пользователь выбирает:
# # - изображение с внедренным ЦВЗ
# # - секретный ключ (для восстановления порядка пикселей)
# # - размеры исходного ЦВЗ (ширина и высота)
# # Результат сохранен по пути /contrast_extract_result/Set{set_number}/{result}


from PIL import Image
from pathlib import Path
import random
import json
from constants import SET_MESSAGE


def extract_contrast(container_path, output_path, key, mask_path):
    """
    Извлекает ЦВЗ из изображения-контейнера, используя сохраненную маску
    """
    container = Image.open(container_path).convert('L')

    # Загружаем маску
    with open(mask_path, 'r') as f:
        mask_data = json.load(f)

    mask = mask_data['mask']
    width = mask_data['width']
    height = mask_data['height']
    total_watermark_bits = mask_data['total_bits']

    print(f"Всего бит для извлечения: {total_watermark_bits}")

    pixels = container.load()

    # Формируем список пикселей с их битами из маски
    pixel_info = []
    for y in range(height):
        for x in range(width):
            bits_to_extract = mask[y][x]
            pixel_info.append((x, y, bits_to_extract))

    random.seed(key)
    random.shuffle(pixel_info)

    # Извлекаем биты
    extracted_bits = []
    bit_index = 0

    for x, y, bits_to_extract in pixel_info:
        if bit_index >= total_watermark_bits:
            break

        pixel = pixels[x, y]

        for b in range(bits_to_extract):
            if bit_index + b < total_watermark_bits:
                extracted_bit = (pixel >> b) & 1
                extracted_bits.append(extracted_bit)

        bit_index += bits_to_extract

    print(f"Извлечено бит: {len(extracted_bits)}")

    # Преобразуем биты обратно в пиксели (по 8 бит на пиксель)
    watermark_pixels = []
    for i in range(0, len(extracted_bits), 8):
        if i + 8 <= len(extracted_bits):
            byte_bits = ''.join(str(bit) for bit in extracted_bits[i:i + 8])
            watermark_pixels.append(int(byte_bits, 2))

    print(f"Получено пикселей: {len(watermark_pixels)}")

    # Вычисляем размеры изображения ЦВЗ
    watermark_size = int((len(watermark_pixels)) ** 0.5)
    while watermark_size * watermark_size < len(watermark_pixels):
        watermark_size += 1

    watermark_image = Image.new('1', (watermark_size, watermark_size))
    watermark_image.putdata(watermark_pixels[:watermark_size * watermark_size])

    watermark_image.save(output_path)

    return len(extracted_bits), len(watermark_pixels), watermark_size


def main():
    print("Программа извлечения цифрового водяного знака (логотипа) методом адаптации по локальному контрасту")

    set_number = input(SET_MESSAGE)
    folder_path = Path('./contrast_embed_result/Set' + set_number)

    print(f"\nПоиск файлов в папке: {folder_path}")

    key = int(input("Введите секретный ключ (число): "))

    for file in folder_path.iterdir():
        if "_watermarked" in file.stem:
            print(f"\nОбработка файла: {file.name}")

            # Ищем файл маски
            mask_path = file.with_suffix('.mask.json')
            if not mask_path.exists():
                print(f"  Ошибка: не найден файл маски {mask_path}")
                continue

            output_folder = Path(f"./contrast_extract_result/Set{set_number}/")
            output_folder.mkdir(parents=True, exist_ok=True)
            output_path = output_folder / f"{file.stem}_extracted.bmp"

            extracted_bits, pixel_count, wm_size = extract_contrast(file, output_path, key, mask_path)

            container = Image.open(file).convert('L')
            container_capacity = container.width * container.height

            print(f"\nРезультат:")
            print(f"  Размер контейнера {container_capacity} пикселей")
            print(f"  Извлечено бит: {extracted_bits}")
            print(f"  Размер извлеченного ЦВЗ: {pixel_count} пикселей")
            print(f"  Сохранено: {output_path}")


if __name__ == "__main__":
    main()