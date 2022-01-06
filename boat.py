import math

import pygame
import os


size = width, height = 1000, 800
all_sprites = pygame.sprite.Group()
river_sprites = pygame.sprite.Group()
beach_size = 1000
river_size = 1000

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


    def update(self, beach1, beach2, river):
        if not pygame.sprite.collide_mask(self, beach1):
            exit()
        if pygame.sprite.collide_mask(self, beach1) or pygame.sprite.collide_mask(self, beach2):
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

class Beach(River):
    def __init__(self, polygon, site):
        super(River, self).__init__(river_sprites)
        self.image = pygame.Surface([5000, 5000], pygame.SRCALPHA, 32)
        if site == 'right':
            polygon = [(beach_size, beach_size)] + polygon
            polygon = polygon + [(beach_size, 0)]
        if site == 'left':
            polygon = [(0, beach_size)] + polygon
            polygon = polygon + [(0, 0)]
        print(polygon)
        pygame.draw.polygon(self.image, 'orange', (polygon))
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)


boat_image = load_image('boat.png')
x, y = boat_image.get_size()
speed = 5


def boat_run():
    pygame.init()
    multiplier = 1
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("boat")
    screen.fill('blue')
    river = River()  # сюда полигон реки
    beach1 = Beach() # сюда правого берега
    beach2 = Beach() # сюда левого береша
    boat = Boat(boat_image)
    all_sprites.add(boat)
    clock = pygame.time.Clock()
    running = True
    allow_right = False
    allow_left = False
    allow_up = False
    allow_down = False
    cnt = 200
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
            river.move('up', boat.angle)
        if allow_down:
            beach1.move('down', boat.angle)
            beach2.move('down', boat.angle)
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
        if cnt > 0:
            cnt -= 1
        else:
            boat.update(beach1, beach2, river)
        river_sprites.draw(screen)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()


boat_run()