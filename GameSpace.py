import os
import sys
import pygame

pygame.init()
FPS = 20

WIDTH = 900
HEIGHT = 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
water_group = pygame.sprite.Group()
bivers = pygame.sprite.Group()


def load_image(name, color_key=None, way_to_file="try\\left"):
    fullname = os.path.join(way_to_file, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def make_kamushi(*args, s=20):
    points = args[0]
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i + 1]
        dx = p1[0] - p2[0]
        if dx == 0:
            continue
        dy = p1[1] - p2[1]
        ras = int((dx**2 + dy**2) ** 0.5)
        for j in range(ras // s):
            KAMUSHI(int(p1[0] - j * (dx / (ras / s)) - s), int(p1[1] - j * (dy / (ras / s)) - 3 * s), 3 * s, 4.5 * s)


class KAMUSHI(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, creat=True):
        super().__init__(bivers)
        self.x, self.y, self.w, self.h = x, y, w, h
        self.frames = []
        self.cur_frame = 0
        # if creat:
        #     self.creating_images()
        self.load_animation()
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def load_animation(self):
        self.rect = pygame.Rect((0, 0), (self.w, self.h))
        for i in range(16):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png", way_to_file="камышы")
            sheet = pygame.transform.scale(sheet, (self.w, self.h))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        for i in range(15, 0, -1):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png", way_to_file="камышы")
            sheet = pygame.transform.scale(sheet, (self.w, self.h))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        pass


class BOAT(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__(all_sprites)
        self.x, self.y, self.w, self.h = x, y, w, h
        self.frames = []
        self.cur_frame = 0
        self.creating_images()
        self.load_animation()
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def creating_images(self):

        from PIL import Image

        for i in range(11, 29):
            im = Image.open(f'лодка с качественной анимацией\\{i}.png')
            im2 = im.crop((335, 400, 863, 1340))
            im2.save(f'try\\left\\{i - 10}.png')
            im4 = im2.transpose(Image.FLIP_LEFT_RIGHT)
            im4.save(f'try\\right\\{i - 10}.png')
            im3 = im2.transpose(Image.FLIP_TOP_BOTTOM)
            im3.save(f'try\\\left\\{18 * 2 - i + 10}.png')
            im5 = im3.transpose(Image.FLIP_LEFT_RIGHT)
            im5.save(f'try\\right\\{18 * 2 - i + 10}.png')

        for i in range(29, 38):
            im = Image.open(f'лодка с качественной анимацией\\{i}.png')
            im2 = im.crop((335, 400, 863, 1340))
            im2.save(f'try\\change\\{i - 28}.png')
            im4 = im2.transpose(Image.FLIP_LEFT_RIGHT)
            im4.save(f'try\\change\\{18 - i + 28}.png')

    def load_animation(self):
        self.rect = pygame.Rect((0, 0), (self.w, self.h))

        for i in range(10, 36):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png")
            sheet = pygame.transform.scale(sheet, (self.w, self.h))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        for i in range(1, 10):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png")
            sheet = pygame.transform.scale(sheet, (self.w, self.h))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        for i in range(1, 18):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png", way_to_file="try\\change")
            sheet = pygame.transform.scale(sheet, (self.w, self.h))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        for i in range(10, 36):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png", way_to_file="try\\right")
            sheet = pygame.transform.scale(sheet, (self.w, self.h))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        for i in range(1, 10):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png", way_to_file="try\\right")
            sheet = pygame.transform.scale(sheet, (self.w, self.h))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        for i in range(17, 0, -1):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png", way_to_file="try\\change")
            sheet = pygame.transform.scale(sheet, (self.w, self.h))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class WATER(pygame.sprite.Sprite):
    image = load_image("water.jpg", way_to_file="other_pictures")

    def __init__(self, *args):
        super().__init__(water_group)
        self.image = WATER.image
        self.rect = self.image.get_rect()
        self.points = list(args)
        pygame.draw.polygon(screen, pygame.Color("pink"), self.points)
        self.mask = pygame.mask.from_threshold(screen, pygame.Color("pink"))

    def update(self):
        pass


class GreenSpace:
    def __init__(self, water_class):
        self.water_class = water_class
        self.points = self.water_class.points.copy()
        self.points.append((0, 0))
        self.points.append((0, HEIGHT))
        self.points.append((WIDTH, HEIGHT))
        self.points.append((WIDTH, 0))

    def update(self):
        pygame.draw.polygon(screen, pygame.Color("green"), self.points)


water = WATER((200, 0), (100, 450), (200, 900), (700, 900), (600, 450),  (700, 0))
boat = BOAT(400, 600, 100, 200)
green = GreenSpace(water)
make_kamushi(water.points)

# Главный Игровой цикл
running = True
while running:
    WIDTH, HEIGHT = pygame.display.get_window_size()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color("pink"))
    water_group.draw(screen)
    water_group.update()
    green.update()
    all_sprites.draw(screen)
    all_sprites.update()
    bivers.draw(screen)
    bivers.update()
    pygame.display.flip()
    clock.tick(FPS)
