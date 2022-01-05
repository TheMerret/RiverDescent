import math

import pygame
import os


size = width, height = 1000, 800
all_sprites = pygame.sprite.Group()
river_sprites = pygame.sprite.Group()

def load_image(path):
    full_path = os.path.join('data', path)
    if not os.path.exists(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        exit()
    im = pygame.image.load(full_path)
    return im


class Boat(pygame.sprite.Sprite):
    def __init__(self, boat_image):
        super(Boat, self).__init__(all_sprites)
        self.image = boat_image
        self.rect = self.image.get_rect()
        self.rect.x = width // 2 - x / 2
        self.rect.y = height // 2 - y / 2
        self.angle = 0
        self.x = width // 2
        self.y = height // 2
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

    def rotate(self):
        boat_temp_image = pygame.transform.rotate(boat_image, self.angle)
        new_rect = boat_temp_image.get_rect(center=(self.x, self.y))
        self.image = boat_temp_image
        self.rect = new_rect


    def update(self, river):
        if not pygame.sprite.collide_mask(self, river):
            exit()


class River(pygame.sprite.Sprite):
    def __init__(self, polygon):
        super(River, self).__init__(river_sprites)
        self.image = pygame.Surface([5000,5000], pygame.SRCALPHA, 32)
        pygame.draw.polygon(self.image, 'blue', (polygon))
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, site, angle, multiplier=1):
        a = math.radians(angle)
        b = math.radians(angle)
        if site == 'down':
            self.rect.x -= math.sin(a) * speed * multiplier
            self.rect.y -= math.cos(b) * speed * multiplier
        if site == 'up':
            self.rect.x += math.sin(a) * speed * multiplier
            self.rect.y += math.cos(b) * speed * multiplier


boat_image = load_image('boat.png')
x, y = boat_image.get_size()
speed = 5


def boat_run():
    pygame.init()
    multiplier = 1
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("boat")
    screen.fill('orange')
    river = River([(465, 188), (864, 224), (837, 527), (974, 718), (1267, 688), (1807, 1372), (1988, 1391), (2056, 1461), (2072, 1488), (2147, 1578), (2153, 2504), (2202, 2586), (2159, 2891), (2136, 2984), (2432, 3246), (2456, 3367), (2449, 3402), (2567, 3612), (2869, 3852), (2878, 4077), (3404, 4104), (3598, 4605), (3531, 5016), (3136, 4952), (3185, 4648), (3125, 4490), (2493, 4458), (2477, 4051), (2257, 3877), (2029, 3470), (2037, 3431), (1690, 3123), (1765, 2816), (1786, 2668), (1724, 2563), (1754, 2507), (1749, 1768), (1597, 1752), (1089, 1108), (784, 1139), (425, 638), (465, 188)])  # example
    boat = Boat(boat_image)
    all_sprites.add(boat)
    clock = pygame.time.Clock()
    running = True
    allow_right = False
    allow_left = False
    allow_up = False
    allow_down = False
    while running:
        boat.rotate()
        screen.fill('orange')
        if allow_left:
            boat.angle += 2
        if allow_right:
            boat.angle -= 2
        if allow_up:
            river.move('up', boat.angle)
        if allow_down:
            river.move('down', boat.angle)
        #if sliding and multiplier > 0:
        #    river.move(direction, boat.angle, multiplier)
        #    multiplier -= 0.01
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not allow_right:
                    allow_left = True
                if event.key == pygame.K_RIGHT and not allow_left:
                    allow_right = True
                if event.key == pygame.K_UP and not allow_down:
                    allow_up = True
                if event.key == pygame.K_DOWN and not allow_up:
                    allow_down = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    allow_right = False
                if event.key == pygame.K_LEFT:
                    allow_left = False
                if event.key == pygame.K_UP:
                    allow_up = False
                if event.key == pygame.K_DOWN:
                    allow_down = False
        boat.update(river)
        river_sprites.draw(screen)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()


boat_run()