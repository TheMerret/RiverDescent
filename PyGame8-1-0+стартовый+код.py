import os
import sys
import pygame

pygame.init()
FPS = 7

WIDTH = 600
HEIGHT = 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('ложочка', name)
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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, 600,
                                900)
        for i in range(1, 4):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png")
            sheet = pygame.transform.scale(sheet, (600, 900))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

        for i in range(3, 0, - 1):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png")
            sheet = pygame.transform.scale(sheet, (600, 900))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

        for i in range(12, 9, -1):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png")
            sheet = pygame.transform.scale(sheet, (600, 900))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

        for i in range(10, 13):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png")
            sheet = pygame.transform.scale(sheet, (600, 900))
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


dragon = AnimatedSprite(load_image("1.png"), 8, 2, 50, 50)

# Главный Игровой цикл
running = True
while running:
    WIDTH, HEIGHT = pygame.display.get_window_size()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color(0, 0, 0))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(FPS)
