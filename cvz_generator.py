# функция для генерации ЦВЗ

from PIL import Image, ImageDraw

# Делаем ЦВЗ 150x150
# 150x150 = 22500 пикселей = 180000 бит

img = Image.new('1', (150, 150), 1)
draw = ImageDraw.Draw(img)

# Простой узор
draw.rectangle([0, 0, 150, 150], outline=0, fill=1)
draw.rectangle([30, 30, 120, 120], outline=0, fill=0)
draw.rectangle([50, 50, 100, 100], outline=0, fill=1)

img.save('watermark.bmp')