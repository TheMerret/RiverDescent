import math
import os

import pygame

from river_generation.main import RiverGeneration

size = width, height = 1000, 800
all_sprites = pygame.sprite.Group()
river_sprites = pygame.sprite.Group()
beach_size = 5000
river_size = 10000
river_curvature = 5000


def load_image(path):
    full_path = os.path.join('data', path)
    if not os.path.exists(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        exit()
    im = pygame.image.load(full_path)
    return im


boat_image = load_image('boat.png')
boat_width, boat_height = boat_image.get_size()
speed = 5


class Boat(pygame.sprite.Sprite):
    def __init__(self, boat_image):
        super(Boat, self).__init__(all_sprites)
        self.image = boat_image
        self.rect = self.image.get_rect()
        self.rect.x = width // 2 - boat_width / 2
        self.rect.y = height // 2 - boat_height / 2
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
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, beach1, beach2):
        if pygame.sprite.collide_mask(self, beach1) or pygame.sprite.collide_mask(self, beach2):
            exit()


class River(pygame.sprite.Sprite):
    def __init__(self, polygon):
        super(River, self).__init__(river_sprites)
        self.image = pygame.Surface([5000, 5000], pygame.SRCALPHA, 32)
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


class Beach(River):
    def __init__(self, polygon, site):
        super(River, self).__init__(river_sprites)
        self.image = pygame.Surface([10000, 10000], pygame.SRCALPHA, 32)
        if site == 'left':
            polygon = [(beach_size, 0)] + polygon
            polygon = polygon + [(beach_size * 2, beach_size * 2)]
            for i in range(len(polygon)):
                polygon[i] = (polygon[i][0] + 100, polygon[i][1])
        if site == 'right':
            polygon = [(0, beach_size)] + polygon
            polygon = polygon + [(0, 0)]
        pygame.draw.polygon(self.image, 'orange', (polygon))
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)


def boat_run():
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("boat")
    screen.fill('blue')
    boat = Boat(boat_image)
    rg = RiverGeneration(river_size, river_curvature)
    river_geom = rg.get_river_geom(boat_width, True)
    # import matplotlib.pyplot as plt
    # plt.gca().set_aspect('equal')
    # plt.plot(*zip(*river_geom.path), color='green')
    # plt.plot(*zip(*river_geom.left_bank), color='red')
    # plt.plot(*zip(*river_geom.right_bank), color='blue')
    # plt.show()
    pol1, pol2 = river_geom.left_bank, river_geom.right_bank
    delta_x = pol1[0][0] - boat.x
    delta_y = pol1[0][1] - boat.y
    # FIXME: берега сами пересекаются
    beach1 = Beach(pol1, 'right')  # сюда правого берега
    beach2 = Beach(pol2, 'left')  # сюда левого береша
    beach1.rect.x = -delta_x - 300
    beach2.rect.x = -delta_x - 150
    beach1.rect.y = -delta_y
    beach2.rect.y = -delta_y
    all_sprites.add(boat)
    clock = pygame.time.Clock()
    running = True
    allow_right = False
    allow_left = False
    allow_up = False
    allow_down = False
    cnt = 1000
    while running:
        boat.rotate()
        screen.fill('blue')
        if allow_left:
            boat.angle += 2
        if allow_right:
            boat.angle -= 2
        if allow_up:
            beach1.move('up', boat.angle)
            beach2.move('up', boat.angle)
            # river.move('up', boat.angle)
        if allow_down:
            beach1.move('down', boat.angle)
            beach2.move('down', boat.angle)
            # river.move('down', boat.angle)
        # if sliding and multiplier > 0:
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
        if cnt > 0:
            cnt -= 1
        else:
            boat.update(beach1, beach2)
        river_sprites.draw(screen)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()


boat_run()
