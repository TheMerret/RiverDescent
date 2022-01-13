import math
import os
import random

import pygame

from river_generation import RiverGeneration, ObstaclesGeneration

size = width, height = 1000, 800
all_sprites = pygame.sprite.Group()
river_sprites = pygame.sprite.Group()
obst_sprites = pygame.sprite.Group()
river_size = 10000
river_width = 300
river_curvature = 10000


def load_image(path):
    full_path = os.path.join('assets', path)
    if not os.path.exists(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        exit()
    im = pygame.image.load(full_path)
    return im

speed = 5


class Boat(pygame.sprite.Sprite):
    def __init__(self):
        super(Boat, self).__init__(all_sprites)
        self.frame = 1
        self.image = pygame.transform.scale(load_image(f'boat/change/{self.frame}.png'), (150, 300))
        self.rect = self.image.get_rect()
        self.boat_image = self.image
        self.rect.x = width // 2 - 150 / 2
        self.rect.y = height // 2 - 300 / 2
        self.angle = 0
        self.x = width // 2
        self.y = height // 2
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

    def rotate(self):
        im = pygame.transform.scale(self.boat_image, (150, 300))
        boat_temp_image = pygame.transform.rotate(im, self.angle)
        new_rect = boat_temp_image.get_rect(center=(self.x, self.y))
        self.image = boat_temp_image
        self.rect = new_rect
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, beach1, beach2, obsts):
        if pygame.sprite.collide_mask(self, beach1) or pygame.sprite.collide_mask(self, beach2):
            exit()
        for i in obsts:
            if pygame.sprite.collide_mask(self, i):
                exit()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, rect):
        super(Obstacle, self).__init__(obst_sprites)
        a = random.choice(['hut/хатка5.1.png', 'smallstone/smallstone.png', 'bigstone/bigstoun.png'])
        self.image = load_image(f'barriers/{a}')
        if a == 'smallstone/smallstone.png':
            self.image = pygame.transform.scale(self.image, (40, 40))
        elif a == 'hut/хатка5.1.png':
            self.image = pygame.transform.scale(self.image, (70, 70))
        else:
            self.image = pygame.transform.scale(self.image, (60, 60))
        self.image = pygame.transform.rotate(self.image, random.randint(-360, 360))
        self.rect = self.image.get_rect()
        self.rect.x = round(rect[0][0], 0)
        self.rect.y = round(rect[0][1], 0)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, site, angle, multiplier=2):
        a = math.radians(angle)
        b = math.radians(angle)
        if site == 'down':
            self.rect.x -= math.sin(a) * speed * multiplier
            self.rect.y -= math.cos(b) * speed * multiplier
        if site == 'up':
            self.rect.x += round(math.sin(a) * speed * multiplier, 0)
            self.rect.y += round(math.cos(b) * speed * multiplier, 0)


class Finish(pygame.sprite.Sprite):
    def __init__(self):
        super(Finish, self).__init__(river_sprites)
        self.image = pygame.transform.scale(load_image('finish.png'), (river_size, 100))
        self.rect = self.image.get_rect()
        self.rect.y = -river_size
        self.mask = pygame.mask.from_surface(self.image)



class River(pygame.sprite.Sprite):
    def __init__(self, polygon):
        super(River, self).__init__(river_sprites)
        self.image = pygame.Surface([5000, 5000], pygame.SRCALPHA, 32)
        pygame.draw.polygon(self.image, 'blue', (polygon))
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, site, angle, multiplier=2):
        a = math.radians(angle)
        b = math.radians(angle)
        if site == 'down':
            self.rect.x -= math.sin(a) * speed * multiplier
            self.rect.y -= math.cos(b) * speed * multiplier
        if site == 'up':
            self.rect.x += round(math.sin(a) * speed * multiplier, 0)
            self.rect.y += round(math.cos(b) * speed * multiplier, 0)


class Beach(River):
    def __init__(self, polygon, site):
        super(River, self).__init__(river_sprites)
        self.image = pygame.Surface([river_size + width, river_size + height], pygame.SRCALPHA, 32)
        if site == 'left':
            polygon = [(river_size + width, river_size)] + [(river_size + width, 0)] + polygon
            for i in range(len(polygon)):
                polygon[i] = (polygon[i][0], polygon[i][1])
        if site == 'right':
            polygon = [(-width, 0)] + [(-width, river_size)] + polygon
        pygame.draw.polygon(self.image, 'orange', (polygon))
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)


def boat_run():
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("boat")
    screen.fill('blue')
    boat = Boat()
    rg = RiverGeneration(river_size, 100)
    river_geom = rg.get_river_geom(river_width, smooth=True)

    og = ObstaclesGeneration(river_geom)
    obstacle_groups = og.get_obstacle_groups()
    obstacles = [obstacle for obstacle_group in obstacle_groups for obstacle
                 in obstacle_group.obstacles]

    for i in obstacles:
        obst = Obstacle(i.normalized_rect)
        obst_sprites.add(obst)

    import matplotlib.pyplot as plt
    plt.gca().set_aspect('equal')
    exterior = river_geom.exterior
    plt.plot(*zip(*exterior))
    for line in og.control_lines:
        plt.plot(*zip(*line), color='orange')
    for group in obstacle_groups:
        for box in group.obstacles:
            plt.plot(*zip(*box.normalized_rect), color='red')
    plt.show()

    a = (river_geom.left_bank, river_geom.right_bank)
    pol1, pol2 = a[0], a[1]
    delta_x = pol1[0][0] - boat.x
    delta_y = pol1[0][1] - boat.y
    beach1 = Beach(pol1, 'right')  # сюда правого берега
    beach2 = Beach(pol2, 'left')  # сюда левого береша
    beach1.rect.x = round(-delta_x - river_width, 0)
    beach2.rect.x = round(-delta_x - river_width, 0)
    beach1.rect.y = round(-delta_y, 0)
    beach2.rect.y = round(-delta_y, 0)
    for i in obst_sprites:
        i.rect.x = i.rect.x - delta_x - river_width
        i.rect.y = i.rect.y - delta_y
    all_sprites.add(boat)
    clock = pygame.time.Clock()
    running = True
    allow_right = False
    allow_left = False
    cnt = 150
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 100)
    num = 3
    allow = False
    textsurface = myfont.render(str(num), False, (255, 255, 255))
    finish = Finish()
    river_sprites.add(finish)
    f = True
    while running:
        if allow:
            if boat.frame < 87 and f:
                boat.frame += 1
            else:
                if boat.frame == 1:
                    f = True
                else:
                    f = False
                    boat.frame -= 1
            boat.image = load_image(f'boat/change/{boat.frame}.png')
            boat.boat_image = boat.image
        boat.rotate()
        screen.fill('blue')
        if pygame.sprite.collide_mask(boat, finish):
            exit()
        if allow_left:
            if boat.angle < 90:
                boat.angle += 2
        if allow_right:
            if boat.angle > - 90:
                boat.angle -= 2
        if allow:
            for i in obst_sprites:
                i.move('up', boat.angle)
            beach1.move('up', boat.angle)
            beach2.move('up', boat.angle)
            finish.rect.x = beach1.rect.x
            finish.rect.y = beach1.rect.y
        elif not allow:
            if cnt > 100:
                textsurface = myfont.render('3', False, (255, 255, 255))
            elif cnt > 50:
                textsurface = myfont.render('2', False, (255, 255, 255))
            elif cnt > 0:
                textsurface = myfont.render('1', False, (255, 255, 255))
            screen.blit(textsurface, (width - 100, height - 150))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not allow_right:
                    allow_left = True
                if event.key == pygame.K_RIGHT and not allow_left:
                    allow_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    allow_right = False
                if event.key == pygame.K_LEFT:
                    allow_left = False
        if cnt > 0:
            cnt -= 1
        else:
            allow = True
            boat.update(beach1, beach2, obst_sprites)
        obst_sprites.draw(screen)
        river_sprites.draw(screen)
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(50)
    pygame.quit()





boat_run()
