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


class Stoun(pygame.sprite.Sprite):
    image = load_image(f"stounversion1small.png", way_to_file="other_pictures")

    def __init__(self, x, y, a):
        super().__init__(all_sprites)
        self.x, self.y, self.w, self.h = x, y, a, a
        self.image = Stoun.image
        self.image = pygame.transform.scale(self.image, (self.w, self.h))
        self.rect = pygame.Rect((0, 0), (self.w, self.h))
        self.rect = self.rect.move(x, y)
        self.image = self.image.subsurface(pygame.Rect((0, 0), self.rect.size))

    def update(self):
        pass


stoun = Stoun(290, 300, 75)


running = True
while running:
    WIDTH, HEIGHT = pygame.display.get_window_size()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color("pink"))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(FPS)
