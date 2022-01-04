from PIL import Image

for i in range(11, 29):
    im = Image.open(f'лодка с качественной анимацией\\{i}.png')
    im2 = im.crop((0, 0, 1200, 1740))
    im2.save(f'try\\left\\{i - 10}.png')
    im4 = im2.transpose(Image.FLIP_LEFT_RIGHT)
    im4.save(f'try\\right\\{i - 10}.png')
    im3 = im2.transpose(Image.FLIP_TOP_BOTTOM)
    im3.save(f'try\\\left\\{18 * 2 - i + 10}.png')
    im5 = im3.transpose(Image.FLIP_LEFT_RIGHT)
    im5.save(f'try\\right\\{18 * 2 - i + 10}.png')
