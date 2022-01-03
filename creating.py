from PIL import Image

for i in range(11, 29):
    im = Image.open(f'лодка с качественной анимацией\\{i}.png')
    im2 = im.crop((0, 0, 1200, 1740))
    im2.save(f'try\\{i - 10}.png')
    im3 = im2.transpose(Image.FLIP_TOP_BOTTOM)
    im3.save(f'try\\{18 * 2 - i + 10}.png')
