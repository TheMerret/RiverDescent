from PIL import Image

for i in range(29, 38):
    im = Image.open(f'лодка с качественной анимацией\\{i}.png')
    im2 = im.crop((0, 0, 1200, 1740))
    im2.save(f'try\\change\\{i - 28}.png')
    im4 = im2.transpose(Image.FLIP_LEFT_RIGHT)
    im4.save(f'try\\change\\{18 - i + 28}.png')