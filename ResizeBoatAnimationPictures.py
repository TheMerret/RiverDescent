from PIL import Image
import os

#for i in range(181):
#    os.mkdir(f"boat2\\{i}")
#    os.mkdir(f"boat2\\{i}\\right")
#    os.mkdir(f"boat2\\{i}\\left")
#    os.mkdir(f"boat2\\{i}\\change")

for i in range(11, 29):
    im = Image.open(f'лодка с качественной анимацией\\{i}.png')
    im1 = im.crop((0, 0, 1200, 1740))
    im1 = im1.resize((300, 435), Image.ANTIALIAS)
    for j in range(181):
        im2 = im1.copy()
        im4 = im2.transpose(Image.FLIP_LEFT_RIGHT)
        im3 = im2.transpose(Image.FLIP_TOP_BOTTOM)
        im5 = im3.transpose(Image.FLIP_LEFT_RIGHT)
        im2 = im2.rotate(270 + j)
        im2.save(f'boat2\\{j}\\left\\{i - 10}.png')
        im4 = im4.rotate(270 + j)
        im4.save(f'boat2\\{j}\\right\\{i - 10}.png')
        im3 = im3.rotate(270 + j)
        im3.save(f'boat2\\{j}\\left\\{18 * 2 - i + 10}.png')
        im5 = im5.rotate(270 + j)
        im5.save(f'boat2\\{j}\\right\\{18 * 2 - i + 10}.png')


for i in range(29, 38):
    im = Image.open(f'лодка с качественной анимацией\\{i}.png')
    im1 = im.crop((0, 0, 1200, 1740))
    im1 = im1.resize((300, 435))
    for j in range(181):
        im2 = im1.copy()
        im4 = im2.transpose(Image.FLIP_LEFT_RIGHT)
        im2 = im2.rotate(270 + j)
        im2.save(f'boat2\\{j}\\change\\{i - 28}.png')
        im4 = im4.rotate(270 + j)
        im4.save(f'boat2\\{j}\\change\\{18 - i + 28}.png')
