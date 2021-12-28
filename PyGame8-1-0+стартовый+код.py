import os
import sys
import pygame

pygame.init()
FPS = 20

WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('куст с ягодами анимация', name)
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
        self.rect = pygame.Rect(0, 0, 261,
                                300)
        for i in range(1, 19):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png")
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        for i in range(5):
            frame_location = (0, 0)
            sheet = load_image(f"18.png")
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        for i in range(18, 0, -1):
            frame_location = (0, 0)
            sheet = load_image(f"{i}.png")
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
